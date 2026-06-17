import os
from datetime import timedelta
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from chat.models import Conversation, Message
from credits.models import CreditApplication, calculate_eligibility_score, generate_repayment_schedule
from insurance.models import InsuranceProduct, InsuranceSubscription
from notifications.models import Notification
from repayments.models import Repayment, RepaymentSchedule

User = get_user_model()


class Command(BaseCommand):
    help = "Charge des données de démonstration pour COFINANCE CI"

    def handle(self, *args, **options):
        self.stdout.write("Création des utilisateurs...")
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@cofinance.ci",
                "first_name": "Admin",
                "last_name": "COFINANCE",
                "role": User.Role.ADMIN,
                "region": User.Region.ABIDJAN,
                "is_staff": True,
                "is_superuser": True,
                "is_online": True,
            },
        )
        if not admin_user.has_usable_password():
            admin_user.set_password("admin123")
            admin_user.save()

        agent, _ = User.objects.get_or_create(
            username="agent1",
            defaults={
                "email": "agent1@cofinance.ci",
                "first_name": "Kouadio",
                "last_name": "Yao",
                "role": User.Role.AGENT,
                "region": User.Region.ABIDJAN,
                "phone": "+2250700000001",
                "is_online": True,
            },
        )
        if not agent.has_usable_password():
            agent.set_password("agent123")
            agent.save()

        client1, _ = User.objects.get_or_create(
            username="client1",
            defaults={
                "email": "client1@example.ci",
                "first_name": "Awa",
                "last_name": "Traoré",
                "role": User.Role.CLIENT,
                "region": User.Region.ABIDJAN,
                "phone": "+2250700000101",
            },
        )
        if not client1.has_usable_password():
            client1.set_password("client123")
            client1.save()

        client2, _ = User.objects.get_or_create(
            username="client2",
            defaults={
                "email": "client2@example.ci",
                "first_name": "Moussa",
                "last_name": "Koné",
                "role": User.Role.CLIENT,
                "region": User.Region.BOUAKE,
                "phone": "+2250700000102",
            },
        )
        if not client2.has_usable_password():
            client2.set_password("client123")
            client2.save()

        self.stdout.write("Création des produits d'assurance...")
        products_data = [
            {
                "name": "Assurance Vie Essentielle",
                "product_type": InsuranceProduct.ProductType.LIFE,
                "description": "Couverture vie simplifiée pour micro-entrepreneurs.",
                "premium_amount": Decimal("5000"),
                "coverage_amount": Decimal("500000"),
                "duration_months": 12,
            },
            {
                "name": "Protection Décès-Invalidité",
                "product_type": InsuranceProduct.ProductType.DEATH_DISABILITY,
                "description": "Protection en cas de décès ou invalidité.",
                "premium_amount": Decimal("3000"),
                "coverage_amount": Decimal("300000"),
                "duration_months": 6,
            },
            {
                "name": "Assurance Multirisque Professionnelle",
                "product_type": InsuranceProduct.ProductType.LIFE,
                "description": "Couverture complète pour professionnels.",
                "premium_amount": Decimal("10000"),
                "coverage_amount": Decimal("1000000"),
                "duration_months": 12,
            },
        ]
        products = []
        for pdata in products_data:
            product, _ = InsuranceProduct.objects.get_or_create(name=pdata["name"], defaults=pdata)
            products.append(product)

        self.stdout.write("Création des demandes de crédit...")
        now = timezone.now()

        if not CreditApplication.objects.exists():
            # Crédit 1: client1 - approuvé, décaissé, avec remboursements
            credit1 = CreditApplication.objects.create(
                client=client1,
                amount_requested=Decimal("250000"),
                purpose="Achat de marchandises pour boutique",
                duration_months=6,
                repayment_frequency=CreditApplication.Frequency.MONTHLY,
                status=CreditApplication.Status.DISBURSED,
                eligibility_score=calculate_eligibility_score(client1, Decimal("250000")),
                assigned_agent=agent,
                region=User.Region.ABIDJAN,
                interest_rate=Decimal("0.1200"),
                approved_at=now - timedelta(days=45),
                disbursed_at=now - timedelta(days=40),
            )
            generate_repayment_schedule(credit1)

            # Crédit 2: client2 - en révision
            credit2 = CreditApplication.objects.create(
                client=client2,
                amount_requested=Decimal("150000"),
                purpose="Achat d'intrants agricoles",
                duration_months=4,
                repayment_frequency=CreditApplication.Frequency.WEEKLY,
                status=CreditApplication.Status.IN_REVIEW,
                eligibility_score=calculate_eligibility_score(client2, Decimal("150000")),
                assigned_agent=agent,
                region=User.Region.BOUAKE,
                interest_rate=Decimal("0.1000"),
            )

            # Crédit 3: client1 - soumis
            credit3 = CreditApplication.objects.create(
                client=client1,
                amount_requested=Decimal("100000"),
                purpose="Réparation équipement de boutique",
                duration_months=3,
                repayment_frequency=CreditApplication.Frequency.MONTHLY,
                status=CreditApplication.Status.SUBMITTED,
                eligibility_score=calculate_eligibility_score(client1, Decimal("100000")),
                region=User.Region.ABIDJAN,
            )

            # Crédit 4: client2 - approuvé et décaissé
            credit4 = CreditApplication.objects.create(
                client=client2,
                amount_requested=Decimal("500000"),
                purpose="Agrandissement de l'exploitation agricole",
                duration_months=12,
                repayment_frequency=CreditApplication.Frequency.MONTHLY,
                status=CreditApplication.Status.DISBURSED,
                eligibility_score=calculate_eligibility_score(client2, Decimal("500000")),
                assigned_agent=agent,
                region=User.Region.BOUAKE,
                interest_rate=Decimal("0.1500"),
                approved_at=now - timedelta(days=20),
                disbursed_at=now - timedelta(days=15),
            )
            generate_repayment_schedule(credit4)

            # Crédit 5: client1 - rejeté
            CreditApplication.objects.create(
                client=client1,
                amount_requested=Decimal("1000000"),
                purpose="Financement véhicule",
                duration_months=24,
                repayment_frequency=CreditApplication.Frequency.MONTHLY,
                status=CreditApplication.Status.REJECTED,
                eligibility_score=calculate_eligibility_score(client1, Decimal("1000000")),
                assigned_agent=agent,
                region=User.Region.ABIDJAN,
                rejection_reason="Score d'éligibilité insuffisant pour le montant demandé",
            )
        else:
            credit1 = CreditApplication.objects.filter(client=client1, status=CreditApplication.Status.DISBURSED).first()
            credit4 = CreditApplication.objects.filter(client=client2, status=CreditApplication.Status.DISBURSED).first()

        self.stdout.write("Enregistrement de remboursements...")
        # Remboursements pour credit1 (client1)
        schedules1 = RepaymentSchedule.objects.filter(credit__client=client1).order_by("installment_number")
        for i, schedule in enumerate(schedules1):
            if i == 0 and not Repayment.objects.filter(schedule=schedule).exists():
                Repayment.objects.create(
                    schedule=schedule,
                    amount=schedule.amount_due,
                    payment_method="orange_money",
                    reference=f"OM-C1-{i+1}",
                    recorded_by=agent,
                )
            elif i == 1 and not Repayment.objects.filter(schedule=schedule).exists():
                Repayment.objects.create(
                    schedule=schedule,
                    amount=schedule.amount_due - Decimal("5000"),
                    payment_method="mtn_money",
                    reference=f"MTN-C1-{i+1}",
                    recorded_by=agent,
                    notes="Paiement partiel, solde à régulariser",
                )

        # Remboursements pour credit4 (client2)
        schedules4 = RepaymentSchedule.objects.filter(credit__client=client2).order_by("installment_number")
        for i, schedule in enumerate(schedules4):
            if i == 0 and not Repayment.objects.filter(schedule=schedule).exists():
                Repayment.objects.create(
                    schedule=schedule,
                    amount=schedule.amount_due,
                    payment_method="wave",
                    reference=f"WAVE-C2-{i+1}",
                    recorded_by=agent,
                )

        self.stdout.write("Création des souscriptions assurance...")
        if not InsuranceSubscription.objects.exists():
            start = timezone.now().date()

            # Assurance vie pour client1
            InsuranceSubscription.objects.create(
                client=client1,
                product=products[0],
                start_date=start - relativedelta(months=2),
                end_date=start + relativedelta(months=10),
                premium_paid=products[0].premium_amount,
                policy_number="POL-DEMO001",
                status=InsuranceSubscription.Status.ACTIVE,
            )

            # Protection décès pour client1
            InsuranceSubscription.objects.create(
                client=client1,
                product=products[1],
                start_date=start - relativedelta(months=1),
                end_date=start + relativedelta(months=5),
                premium_paid=products[1].premium_amount,
                policy_number="POL-DEMO002",
                status=InsuranceSubscription.Status.ACTIVE,
            )

            # Multirisque pour client2
            InsuranceSubscription.objects.create(
                client=client2,
                product=products[2],
                start_date=start - relativedelta(months=3),
                end_date=start + relativedelta(months=9),
                premium_paid=products[2].premium_amount,
                policy_number="POL-DEMO003",
                status=InsuranceSubscription.Status.ACTIVE,
            )

        self.stdout.write("Création des notifications...")
        existing_notifs = Notification.objects.count()
        if existing_notifs < 5:
            notifications_data = [
                {
                    "user": client1,
                    "title": "Bienvenue sur COFINANCE CI",
                    "message": "Votre compte a été créé avec succès. Bienvenue !",
                    "notification_type": "welcome",
                },
                {
                    "user": client1,
                    "title": "Crédit approuvé",
                    "message": "Votre demande de 250 000 FCFA a été approuvée.",
                    "notification_type": "credit_approved",
                },
                {
                    "user": client1,
                    "title": "Échéance de remboursement",
                    "message": "Votre prochaine échéance est prévue dans 3 jours.",
                    "notification_type": "repayment_reminder",
                },
                {
                    "user": client2,
                    "title": "Bienvenue sur COFINANCE CI",
                    "message": "Votre compte a été créé avec succès. Bienvenue !",
                    "notification_type": "welcome",
                },
                {
                    "user": client2,
                    "title": "Crédit en révision",
                    "message": "Votre demande de 150 000 FCFA est en cours d'analyse.",
                    "notification_type": "credit_review",
                },
                {
                    "user": agent,
                    "title": "Nouvelle demande de crédit",
                    "message": "Moussa Koné a soumis une demande de 150 000 FCFA.",
                    "notification_type": "new_credit",
                },
                {
                    "user": admin_user,
                    "title": "Rapport hebdomadaire",
                    "message": "3 nouvelles demandes de crédit cette semaine.",
                    "notification_type": "admin_report",
                },
            ]
            for notif_data in notifications_data:
                Notification.objects.get_or_create(
                    user=notif_data["user"],
                    title=notif_data["title"],
                    defaults={
                        "message": notif_data["message"],
                        "notification_type": notif_data["notification_type"],
                    },
                )

        self.stdout.write("Création des conversations de démonstration...")

        # Conversation 1: client1 avec messages
        conv1, created = Conversation.objects.get_or_create(
            client=client1,
            subject="Question sur mon échéancier de remboursement",
            defaults={"agent": agent, "status": Conversation.Status.ASSIGNED},
        )
        if created:
            Message.objects.create(
                conversation=conv1,
                sender=client1,
                content="Bonjour, je souhaiterais des explications sur mon échéancier de remboursement. Ma première échéance est déjà passée, mais j'aimerais connaître le montant exact de la prochaine.",
            )
            Message.objects.create(
                conversation=conv1,
                sender=agent,
                content="Bonjour Awa ! Je comprends votre demande. Votre échéancier prévoit des mensualités de 43 050 FCFA sur 6 mois. La première échéance a bien été enregistrée. La prochaine est prévue dans 28 jours.",
            )
            Message.objects.create(
                conversation=conv1,
                sender=client1,
                content="Merci pour ces informations. Est-ce que je peux rembourser par anticipation si j'ai des rentrées d'argent ?",
            )
            Message.objects.create(
                conversation=conv1,
                sender=agent,
                content="Oui, tout à fait ! Le remboursement anticipé est possible sans pénalités. Vous pouvez passer par Orange Money, MTN Money ou Wave. Je vous envoie le détail par notification.",
            )

        # Conversation 2: client2
        conv2, created = Conversation.objects.get_or_create(
            client=client2,
            subject="Suivi de ma demande de crédit agricole",
            defaults={"agent": agent, "status": Conversation.Status.OPEN},
        )
        if created:
            Message.objects.create(
                conversation=conv2,
                sender=client2,
                content="Bonjour, j'ai déposé une demande de crédit de 150 000 FCFA pour l'achat d'intrants agricoles il y a une semaine. Pourriez-vous me donner des nouvelles ?",
            )

        # Conversation 3: client1 fermée
        conv3, created = Conversation.objects.get_or_create(
            client=client1,
            subject="Demande d'information sur les assurances",
            defaults={"agent": agent, "status": Conversation.Status.CLOSED},
        )
        if created:
            Message.objects.create(
                conversation=conv3,
                sender=client1,
                content="Bonjour, quels sont les produits d'assurance proposés par COFINANCE ?",
            )
            Message.objects.create(
                conversation=conv3,
                sender=agent,
                content="Bonjour Awa. Nous proposons une Assurance Vie Essentielle à 5 000 FCFA/mois avec une couverture de 500 000 FCFA, et une Protection Décès-Invalidité à 3 000 FCFA/mois. Je vois que vous avez déjà souscrit à ces deux produits !",
            )
            Message.objects.create(
                conversation=conv3,
                sender=client1,
                content="En effet, merci pour les informations !",
            )
            Message.objects.create(
                conversation=conv3,
                sender=agent,
                content="N'hésitez pas si vous avez d'autres questions. Bonne journée !",
            )

        self.stdout.write(self.style.SUCCESS("\nDonnées de démonstration chargées avec succès !"))
        self.stdout.write("\nComptes de test :")
        self.stdout.write("  Admin  : admin / admin123")
        self.stdout.write("  Agent  : agent1 / agent123")
        self.stdout.write("  Client : client1 / client123")
        self.stdout.write("  Client : client2 / client123")
