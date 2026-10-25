import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const api = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' },
    timeout: 10000,
})

export const AnimalsAPI = {
    list: (params) => api.get('/animals', { params }).then(r => r.data),
    get: (id) => api.get(`/animals/${id}`).then(r => r.data),
    create: (data) => api.post('/animals', data).then(r => r.data),
    update: (id, data) => api.put(`/animals/${id}`, data).then(r => r.data),
    patch: (id, data) => api.patch(`/animals/${id}`, data).then(r => r.data),
    remove: (id) => api.delete(`/animals/${id}`),
    adopt: (id) => api.post(`/animals/${id}/adopt`).then(r => r.data),
    stats: () => api.get('/animals/stats').then(r => r.data),
}

export function extractError(err) {
    const detail = err?.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
        return detail
            .map(e => `${(e.loc ?? []).slice(1).join('.')}: ${e.msg}`)
            .join('; ')
    }
    return err?.message || 'Ошибка сети'
}