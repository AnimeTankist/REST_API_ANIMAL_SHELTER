export const SPECIES = [
    { value: 'dog', label: 'Собака' },
    { value: 'cat', label: 'Кошка' },
    { value: 'rabbit', label: 'Кролик' },
    { value: 'bird', label: 'Птица' },
    { value: 'rodent', label: 'Грызун' },
    { value: 'other', label: 'Другое' },
]

export const STATUSES = [
    { value: 'available', label: 'Ищет хозяина' },
    { value: 'reserved', label: 'Забронировано' },
    { value: 'treatment', label: 'На лечении' },
    { value: 'adopted', label: 'Передано' },
]

export const GENDERS = [
    { value: 'male', label: 'Самец' },
    { value: 'female', label: 'Самка' },
    { value: 'unknown', label: 'Неизвестно' },
]

export const SPECIES_LABEL = Object.fromEntries(SPECIES.map(s => [s.value, s.label]))
export const STATUS_LABEL = Object.fromEntries(STATUSES.map(s => [s.value, s.label]))
export const GENDER_LABEL = Object.fromEntries(GENDERS.map(s => [s.value, s.label]))