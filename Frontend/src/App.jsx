import { Link, NavLink, Route, Routes } from 'react-router-dom'
import AnimalsListPage from './pages/AnimalsListPage.jsx'
import AnimalFormPage from './pages/AnimalFormPage.jsx'
import AnimalDetailsPage from './pages/AnimalDetailsPage.jsx'

export default function App() {
    return (
        <div className="app">
            <header className="topbar">
                <div className="container topbar-inner">
                    <Link to="/" className="brand">🐾 Приют «Верный друг»</Link>
                    <nav>
                        <NavLink to="/" end>Список</NavLink>
                        <NavLink to="/animals/new">Добавить</NavLink>
                    </nav>
                </div>
            </header>
            <main className="container">
                <Routes>
                    <Route path="/" element={<AnimalsListPage />} />
                    <Route path="/animals/new" element={<AnimalFormPage />} />
                    <Route path="/animals/:id" element={<AnimalDetailsPage />} />
                    <Route path="/animals/:id/edit" element={<AnimalFormPage />} />
                    <Route path="*" element={<div className="empty">Страница не найдена</div>} />
                </Routes>
            </main>
        </div>
    )
}