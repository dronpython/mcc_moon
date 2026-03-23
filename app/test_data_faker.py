"""
Полное наполнение базы данных с использованием Faker
Запуск: python -m app.seed_faker
"""

import sys
import os
import random
import logging
from typing import List, Dict, Optional
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from faker import Faker
from app.database import SessionLocal, engine
from app import models, schemas, crud

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/seed.log')
    ]
)
logger = logging.getLogger(__name__)

fake = Faker(['ru_RU', 'en_US'])

class DatabaseSeeder:
    def __init__(self, db: Session):
        self.db = db
        self.buildings = []
        self.activities = {}
        self.organizations = []

        # Конфигурация
        self.config = {
            'buildings_count': int(os.getenv('DEFAULT_BUILDINGS', 50)),
            'organizations_count': int(os.getenv('DEFAULT_ORGANIZATIONS', 200)),
            'max_phone_numbers': 3,
            'max_activities_per_org': 4,
        }

    def generate_russian_phone(self) -> str:
        """Генерация российского номера"""
        formats = [
            '+7 ({}{}{}) {}{}{}-{}{}-{}{}',
            '8-{}{}{}-{}{}{}-{}{}-{}{}',
            '+7 {}{}{} {}{}{}-{}{}-{}{}',
            '8-{}{}{}-{}{}-{}{}',
        ]
        digits = [str(random.randint(0, 9)) for _ in range(10)]
        return random.choice(formats).format(*digits)

    def generate_address(self) -> str:
        """Генерация адреса"""
        cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"]
        street_types = ["ул.", "пр-т", "пер.", "б-р"]
        streets = ["Ленина", "Мира", "Советская", "Пушкина", "Гагарина"]

        return (f"г. {random.choice(cities)}, "
                f"{random.choice(street_types)} {random.choice(streets)}, "
                f"д. {random.randint(1, 150)}{random.choice(['', f'/{random.randint(1, 10)}'])}")

    def create_buildings(self):
        """Создание зданий"""
        logger.info(f"📦 Создаем {self.config['buildings_count']} зданий...")

        for i in range(self.config['buildings_count']):
            building = models.Building(
                address=self.generate_address(),
                latitude=float(fake.latitude()),
                longitude=float(fake.longitude())
            )
            self.db.add(building)

            if (i + 1) % 10 == 0:
                self.db.flush()
                logger.info(f"  Создано {i + 1} зданий")

        self.db.commit()
        self.buildings = self.db.query(models.Building).all()
        logger.info(f"✅ Создано {len(self.buildings)} зданий")

    def create_activities(self):
        """Создание видов деятельности"""
        logger.info(f"📚 Создаем виды деятельности...")

        # Корневые категории
        root_categories = [
            "Еда и продукты", "Автомобили и транспорт", "IT и технологии",
            "Строительство и ремонт", "Медицина и здоровье", "Образование",
            "Финансы и страхование", "Туризм и отдых"
        ]

        for root in root_categories:
            activity = models.Activity(name=root)
            self.db.add(activity)
            self.db.flush()
            self.activities[root] = activity.id

            # Создаем подкатегории
            sub_count = random.randint(2, 4)
            for _ in range(sub_count):
                sub_name = f"{fake.word().capitalize()} {root.lower()}"
                sub_activity = models.Activity(name=sub_name, parent_id=activity.id)
                self.db.add(sub_activity)
                self.db.flush()
                self.activities[sub_name] = sub_activity.id

        self.db.commit()
        logger.info(f"✅ Создано {len(self.activities)} видов деятельности")

    def create_organizations(self):
        """Создание организаций"""
        logger.info(f"🏢 Создаем {self.config['organizations_count']} организаций...")

        activity_ids = list(self.activities.values())

        for i in range(self.config['organizations_count']):
            building = random.choice(self.buildings)

            # Телефоны
            num_phones = random.randint(1, self.config['max_phone_numbers'])
            phone_numbers = [self.generate_russian_phone() for _ in range(num_phones)]

            # Активности
            num_activities = random.randint(1, min(self.config['max_activities_per_org'], len(activity_ids)))
            selected_activities = random.sample(activity_ids, num_activities)

            # Название
            name = f"{random.choice(['ООО', 'АО', 'ИП'])} '{fake.company()}'"

            organization = models.Organization(
                name=name,
                building_id=building.id,
                phone_numbers=','.join(phone_numbers)
            )
            self.db.add(organization)
            self.db.flush()

            # Добавляем активности
            for act_id in selected_activities:
                self.db.execute(
                    models.organization_activity.insert().values(
                        organization_id=organization.id,
                        activity_id=act_id
                    )
                )

            if (i + 1) % 20 == 0:
                self.db.commit()
                logger.info(f"  Создано {i + 1} организаций")

        self.db.commit()
        self.organizations = self.db.query(models.Organization).all()
        logger.info(f"✅ Создано {len(self.organizations)} организаций")

    def print_statistics(self):
        """Вывод статистики"""
        # Обновляем счетчики
        buildings_count = self.db.query(models.Building).count()
        activities_count = self.db.query(models.Activity).count()
        organizations_count = self.db.query(models.Organization).count()

        # Связи
        links_count = self.db.query(models.organization_activity).count()

        # Телефоны
        all_phones = 0
        for org in self.organizations:
            if org.phone_numbers:
                all_phones += len(org.phone_numbers.split(','))

        print("\n" + "="*60)
        print("📊 СТАТИСТИКА БАЗЫ ДАННЫХ")
        print("="*60)
        print(f"🏢 Зданий: {buildings_count}")
        print(f"📚 Видов деятельности: {activities_count}")
        print(f"🏭 Организаций: {organizations_count}")
        print(f"🔗 Связей организация-деятельность: {links_count}")
        print(f"📞 Всего телефонных номеров: {all_phones}")

        # Географическое покрытие
        if buildings_count > 0:
            lat_min = min(b.latitude for b in self.buildings)
            lat_max = max(b.latitude for b in self.buildings)
            lon_min = min(b.longitude for b in self.buildings)
            lon_max = max(b.longitude for b in self.buildings)
            print(f"\n🌍 Географическое покрытие:")
            print(f"  Широта: от {lat_min:.2f}° до {lat_max:.2f}°")
            print(f"  Долгота: от {lon_min:.2f}° до {lon_max:.2f}°")

        print("="*60)

    def clear_database(self):
        """Очистка базы данных"""
        logger.warning("🗑️  Очистка базы данных...")

        self.db.execute(models.organization_activity.delete())
        self.db.execute(models.Organization.__table__.delete())
        self.db.execute(models.Activity.__table__.delete())
        self.db.execute(models.Building.__table__.delete())

        self.db.commit()
        logger.info("✅ База данных очищена")

    def run(self, clear=False):
        """Запуск наполнения"""
        if clear:
            self.clear_database()

        try:
            self.create_buildings()
            self.create_activities()
            self.create_organizations()
            self.print_statistics()
            logger.info("🎉 База данных успешно наполнена!")
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            self.db.rollback()
            raise

def main():
    """Точка входа"""
    import argparse

    parser = argparse.ArgumentParser(description="Наполнение базы данных")
    parser.add_argument("--clear", action="store_true", help="Очистить перед наполнением")
    parser.add_argument("--buildings", type=int, help="Количество зданий")
    parser.add_argument("--organizations", type=int, help="Количество организаций")

    args = parser.parse_args()

    db = SessionLocal()
    seeder = DatabaseSeeder(db)

    if args.buildings:
        seeder.config['buildings_count'] = args.buildings
    if args.organizations:
        seeder.config['organizations_count'] = args.organizations

    try:
        seeder.run(clear=args.clear)
    finally:
        db.close()

if __name__ == "__main__":
    main()