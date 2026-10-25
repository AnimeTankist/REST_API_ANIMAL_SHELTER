import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { AnimalsAPI, extractError } from '../api'
import { SPECIES, STATUSES, GENDERS } from '../constants'

const EMPTY = {
    name: '', species: 'cat', breed: '', gender: 'unknown',
    age_months: 12, status: 'available', description: '',
    arrival_date: '', adopted_date: '',
}

export default function AnimalFormPage() {
    const { id } = useParams()
    const isEdit = Boolean(id)
    const navigate = useNavigate()

    const [form, setForm] = useState(EMPTY)
    const [loading, setLoading] = useState(isEdit)
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        if (!isEdit) return
        let cancelled = false
        setLoading(true)
        AnimalsAPI.get(id)
            .then(a => {
                if (cancelled) return
                setForm({
                    name: a.name ?? '',
                    species: a.species ?? 'cat',
                    breed: a.breed ?? '',
                    gender: a.gender ?? 'unknown',
                    age_months: a.age_months ?? 0,
                    status: a.status ?? 'available',
                    description: a.description ?? '',
                    arrival_date: a.arrival_date ?? '',
                    adopted_date: a.adopted_date ?? '',
                })
            })
            .catch(e => { if (!cancelled) setError(extractError(e)) })
            .finally(() => { if (!cancelled) setLoading(false) })
        return () => { cancelled = true }
    }, [id, isEdit])

    function handleChange(e) {
        const { name, value, type } = e.target
        setForm(prev => ({
            ...prev,
            [name]: type === 'number' ? (value === '' ? '' : Number(value)) : value,
        }))
    }

    async function handleSubmit(e) {
        e.preventDefault()
        setSaving(true)
        setError('')
        try {
            const payload = {
                name: form.name.trim(),
                species: form.species,
                breed: form.breed.trim() || null,
                gender: form.gender,
                age_months: Number(form.age_months),
                status: form.status,
                description: form.description.trim() || null,
                arrival_date: form.arrival_date || null,
                adopted_date: form.adopted_date || null,
            }

            if (isEdit) {
                await AnimalsAPI.update(id, payload)
                navigate(`/animals/${id}`)
            } else {
                const created = await AnimalsAPI.create(payload)
                navigate(`/animals/${created.id}`)
            }
        } catch (e) {
            setError(extractError(e))
        } finally {
            setSaving(false)
        }
    }

    if (loading) return <div className="loading">Загрузка…</div>

    return (
        <div className="form-page">
            <h2>{isEdit ? `Редактирование #${id}` : 'Добавление животного'}</h2>
            <form className="form" onSubmit={handleSubmit}>
                <div className="form-grid">
                    <label>
                        Кличка *
                        <input name="name" value={form.name} onChange={handleChange} required minLength={1} maxLength={50} />
                    </label>
                    <label>
                        Вид *
                        <select name="species" value={form.species} onChange={handleChange}>
                            {SPECIES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                        </select>
                    </label>
                    <label>
                        Порода
                        <input name="breed" value={form.breed} onChange={handleChange} maxLength={80} />
                    </label>
                    <label>
                        Пол
                        <select name="gender" value={form.gender} onChange={handleChange}>
                            {GENDERS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                        </select>
                    </label>
                    <label>
                        Возраст, мес. *
                        <input name="age_months" type="number" min="0" max="600" value={form.age_months} onChange={handleChange} required />
                    </label>
                    <label>
                        Статус
                        <select name="status" value={form.status} onChange={handleChange}>
                            {STATUSES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                        </select>
                    </label>
                    <label>
                        Дата поступления
                        <input name="arrival_date" type="date" value={form.arrival_date} onChange={handleChange} />
                    </label>
                    <label>
                        Дата передачи
                        <input name="adopted_date" type="date" value={form.adopted_date} onChange={handleChange} />
                    </label>
                </div>
                <label>
                    Описание
                    <textarea name="description" rows={4} maxLength={1000} value={form.description} onChange={handleChange} />
                </label>

                {error && <div className="error">{error}</div>}

                <div className="form-actions">
                    <button type="submit" className="btn btn-primary" disabled={saving}>
                        {saving ? 'Сохранение…' : (isEdit ? 'Сохранить' : 'Создать')}
                    </button>
                    <button type="button" className="btn" onClick={() => navigate(-1)}>Отмена</button>
                </div>
            </form>
        </div>
    )
}