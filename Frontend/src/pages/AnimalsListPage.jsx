import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { AnimalsAPI, extractError } from '../api'
import {
    SPECIES, STATUSES, GENDERS,
    SPECIES_LABEL, STATUS_LABEL, GENDER_LABEL,
} from '../constants'

const DEFAULTS = {
    search: '', species: '', status: '', gender: '',
    min_age: '', max_age: '', sort_by: 'id', order: 'asc',
    limit: '10', offset: '0',
}

function readParams(sp) {
    const out = { ...DEFAULTS }
    for (const key of Object.keys(DEFAULTS)) {
        if (sp.has(key)) out[key] = sp.get(key)
    }
    return out
}

function buildQuery(filters) {
    const query = {}
    for (const [k, v] of Object.entries(filters)) {
        if (v == null || v === '' || String(v) === String(DEFAULTS[k])) continue
        query[k] = v
    }
    return query
}

export default function AnimalsListPage() {
    const [searchParams, setSearchParams] = useSearchParams()
    const filters = useMemo(() => readParams(searchParams), [searchParams])

    const [draftSearch, setDraftSearch] = useState(filters.search)
    const [data, setData] = useState({ items: [], total: 0 })
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => { setDraftSearch(filters.search) }, [filters.search])

    const load = useCallback(async () => {
        setLoading(true)
        setError('')
        try {
            const [page, statistics] = await Promise.all([
                AnimalsAPI.list(buildQuery(filters)),
                AnimalsAPI.stats().catch(() => null),
            ])
            setData(page)
            setStats(statistics)
        } catch (e) {
            setError(extractError(e))
        } finally {
            setLoading(false)
        }
    }, [filters])

    useEffect(() => { load() }, [load])

    function update(next) {
        setSearchParams(buildQuery({ ...filters, ...next }))
    }

    function submitSearch(e) {
        e.preventDefault()
        update({ search: draftSearch.trim(), offset: '0' })
    }

    function resetAll() {
        setDraftSearch('')
        setSearchParams({})
    }

    async function handleDelete(id) {
        if (!window.confirm(`Удалить запись #${id}?`)) return
        try {
            await AnimalsAPI.remove(id)
            load()
        } catch (e) {
            alert(extractError(e))
        }
    }

    const limit = Number(filters.limit)
    const offset = Number(filters.offset)
    const currentPage = Math.floor(offset / limit) + 1
    const totalPages = Math.max(1, Math.ceil(data.total / limit))

    return (
        <div>
            {stats && (
                <div className="stats-bar">
                    <div><span className="stat-label">Всего</span><span className="stat-value">{stats.total}</span></div>
                    <div><span className="stat-label">Средний возраст</span><span className="stat-value">{stats.average_age_months ?? '—'} мес.</span></div>
                    <div><span className="stat-label">Передано за 30 дней</span><span className="stat-value">{stats.adopted_last_30_days}</span></div>
                    {Object.entries(stats.by_status).map(([k, v]) => (
                        <div key={k}><span className="stat-label">{STATUS_LABEL[k] ?? k}</span><span className="stat-value">{v}</span></div>
                    ))}
                </div>
            )}

            <form className="filters" onSubmit={submitSearch}>
                <input
                    type="search"
                    placeholder="Поиск по кличке, породе, описанию…"
                    value={draftSearch}
                    onChange={(e) => setDraftSearch(e.target.value)}
                />
                <select value={filters.species} onChange={(e) => update({ species: e.target.value, offset: '0' })}>
                    <option value="">Все виды</option>
                    {SPECIES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
                <select value={filters.status} onChange={(e) => update({ status: e.target.value, offset: '0' })}>
                    <option value="">Все статусы</option>
                    {STATUSES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
                <select value={filters.gender} onChange={(e) => update({ gender: e.target.value, offset: '0' })}>
                    <option value="">Любой пол</option>
                    {GENDERS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
                <input
                    type="number" min="0" max="600" placeholder="Возраст от, мес."
                    value={filters.min_age}
                    onChange={(e) => update({ min_age: e.target.value, offset: '0' })}
                />
                <input
                    type="number" min="0" max="600" placeholder="Возраст до, мес."
                    value={filters.max_age}
                    onChange={(e) => update({ max_age: e.target.value, offset: '0' })}
                />
                <select value={filters.sort_by} onChange={(e) => update({ sort_by: e.target.value })}>
                    <option value="id">Сортировка: ID</option>
                    <option value="name">Сортировка: Кличка</option>
                    <option value="age_months">Сортировка: Возраст</option>
                    <option value="arrival_date">Сортировка: Дата поступления</option>
                    <option value="status">Сортировка: Статус</option>
                </select>
                <select value={filters.order} onChange={(e) => update({ order: e.target.value })}>
                    <option value="asc">По возрастанию</option>
                    <option value="desc">По убыванию</option>
                </select>
                <button type="submit" className="btn btn-primary">Найти</button>
                <button type="button" className="btn" onClick={resetAll}>Сбросить</button>
            </form>

            {error && <div className="error">{error}</div>}
            {loading && <div className="loading">Загрузка…</div>}

            <div className="cards">
                {data.items.map(animal => (
                    <article key={animal.id} className={`card status-${animal.status}`}>
                        <header>
                            <h3>{animal.name}</h3>
                            <span className="badge">{STATUS_LABEL[animal.status]}</span>
                        </header>
                        <p className="meta">
                            {SPECIES_LABEL[animal.species]} · {animal.breed || 'порода не указана'} · {GENDER_LABEL[animal.gender]}
                        </p>
                        <p className="meta">Возраст: {animal.age_months} мес. · Поступил: {animal.arrival_date}</p>
                        {animal.description && <p className="desc">{animal.description}</p>}
                        <footer>
                            <Link className="btn" to={`/animals/${animal.id}`}>Подробнее</Link>
                            <Link className="btn" to={`/animals/${animal.id}/edit`}>Изменить</Link>
                            <button className="btn btn-danger" onClick={() => handleDelete(animal.id)}>Удалить</button>
                        </footer>
                    </article>
                ))}
                {!loading && data.items.length === 0 && (
                    <div className="empty">Ничего не найдено. Измените фильтры.</div>
                )}
            </div>

            {data.total > 0 && (
                <div className="pagination">
                    <button className="btn" disabled={currentPage <= 1} onClick={() => update({ offset: String(Math.max(0, offset - limit)) })}>
                        ← Назад
                    </button>
                    <span>Страница {currentPage} из {totalPages} · всего {data.total}</span>
                    <button className="btn" disabled={currentPage >= totalPages} onClick={() => update({ offset: String(offset + limit) })}>
                        Вперёд →
                    </button>
                </div>
            )}
        </div>
    )
}