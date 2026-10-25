import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { AnimalsAPI, extractError } from '../api'
import { SPECIES_LABEL, STATUS_LABEL, GENDER_LABEL } from '../constants'

export default function AnimalDetailsPage() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [animal, setAnimal] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        let cancelled = false
        setLoading(true)
        setError('')
        AnimalsAPI.get(id)
            .then(a => { if (!cancelled) setAnimal(a) })
            .catch(e => { if (!cancelled) setError(extractError(e)) })
            .finally(() => { if (!cancelled) setLoading(false) })
        return () => { cancelled = true }
    }, [id])

    async function handleDelete() {
        if (!window.confirm('Удалить запись?')) return
        try {
            await AnimalsAPI.remove(id)
            navigate('/')
        } catch (e) {
            alert(extractError(e))
        }
    }

    async function handleAdopt() {
        try {
            const updated = await AnimalsAPI.adopt(id)
            setAnimal(updated)
        } catch (e) {
            alert(extractError(e))
        }
    }

    if (loading) return <div className="loading">Загрузка…</div>
    if (error) return <div className="error">{error}</div>
    if (!animal) return null

    const canAdopt = animal.status !== 'adopted'

    return (
        <div>
            <Link to="/" className="back-link">← К списку</Link>
            <article className="details-card">
                <header>
                    <h2>{animal.name}</h2>
                    <span className="badge">{STATUS_LABEL[animal.status]}</span>
                </header>
                <dl>
                    <dt>Вид</dt><dd>{SPECIES_LABEL[animal.species]}</dd>
                    <dt>Порода</dt><dd>{animal.breed || '—'}</dd>
                    <dt>Пол</dt><dd>{GENDER_LABEL[animal.gender]}</dd>
                    <dt>Возраст</dt><dd>{animal.age_months} мес.</dd>
                    <dt>Дата поступления</dt><dd>{animal.arrival_date}</dd>
                    <dt>Дата передачи</dt><dd>{animal.adopted_date || '—'}</dd>
                    <dt>Создано</dt><dd>{new Date(animal.created_at).toLocaleString('ru-RU')}</dd>
                    <dt>Обновлено</dt><dd>{new Date(animal.updated_at).toLocaleString('ru-RU')}</dd>
                </dl>
                {animal.description && <p className="desc">{animal.description}</p>}
                <footer className="actions">
                    <Link className="btn btn-primary" to={`/animals/${id}/edit`}>Редактировать</Link>
                    <button className="btn" onClick={handleAdopt} disabled={!canAdopt}>
                        {canAdopt ? 'Передать хозяину' : 'Уже передано'}
                    </button>
                    <button className="btn btn-danger" onClick={handleDelete}>Удалить</button>
                </footer>
            </article>
        </div>
    )
}