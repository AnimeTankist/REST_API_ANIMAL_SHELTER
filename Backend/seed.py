"""Наполнение БД демонстрационными данными: python seed.py"""
from datetime import date, timedelta

from sqlalchemy import func, select

from app.database import Base, SessionLocal, engine
from app.models import Animal, Gender, Species, Status

TODAY = date.today()

DEMO_ANIMALS = [
    dict(name="Барсик", species=Species.cat, breed="Домашняя короткошёрстная",
         gender=Gender.male, age_months=18, status=Status.available,
         description="Ласковый, приучен к лотку", arrival_date=TODAY - timedelta(days=40)),
    dict(name="Мурка", species=Species.cat, breed="Британская", gender=Gender.female,
         age_months=30, status=Status.reserved, description="Спокойная, стерилизована",
         arrival_date=TODAY - timedelta(days=90)),
    dict(name="Рекс", species=Species.dog, breed="Немецкая овчарка", gender=Gender.male,
         age_months=48, status=Status.available, description="Знает команды, дружелюбный",
         arrival_date=TODAY - timedelta(days=120)),
    dict(name="Белка", species=Species.dog, breed="Дворняга", gender=Gender.female,
         age_months=12, status=Status.adopted, description="Активная, любит прогулки",
         arrival_date=TODAY - timedelta(days=80), adopted_date=TODAY - timedelta(days=10)),
    dict(name="Кеша", species=Species.bird, breed="Волнистый попугай", gender=Gender.male,
         age_months=8, status=Status.available, description="Разговорчивый",
         arrival_date=TODAY - timedelta(days=20)),
    dict(name="Снежок", species=Species.rabbit, breed="Белый великан", gender=Gender.male,
         age_months=14, status=Status.treatment, description="На лечении после травмы",
         arrival_date=TODAY - timedelta(days=5)),
    dict(name="Люся", species=Species.rodent, breed="Джунгарский хомяк", gender=Gender.female,
         age_months=6, status=Status.available, description="Ручная, активная",
         arrival_date=TODAY - timedelta(days=15)),
    dict(name="Тайсон", species=Species.dog, breed="Стаффордширский терьер", gender=Gender.male,
         age_months=36, status=Status.adopted, description="Добрый, но требует опыта",
         arrival_date=TODAY - timedelta(days=200), adopted_date=TODAY - timedelta(days=45)),
    dict(name="Плюша", species=Species.cat, breed="Шотландская вислоухая", gender=Gender.female,
         age_months=24, status=Status.available, description="Общительная, игривая",
         arrival_date=TODAY - timedelta(days=60)),
    dict(name="Найда", species=Species.dog, breed="Лабрадор", gender=Gender.female,
         age_months=60, status=Status.reserved, description="Спокойная, хорошо с детьми",
         arrival_date=TODAY - timedelta(days=150)),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        existing = db.scalar(select(func.count()).select_from(Animal)) or 0
        if existing:
            print(f"В базе уже {existing} записей — сидирование пропущено.")
            return
        db.add_all([Animal(**item) for item in DEMO_ANIMALS])
        db.commit()
    print(f"Добавлено животных: {len(DEMO_ANIMALS)}")


if __name__ == "__main__":
    main()