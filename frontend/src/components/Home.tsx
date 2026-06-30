import React from "react"
import { useNavigate, Outlet } from "react-router"
import '../styles/Home.css';
import iplLogo from "../assets/iplLogo.png"

export function Home() {
    const navigate = useNavigate();

    return (
        <div className="layout-wrapper">
            <header className="site-header">
                <div className="logo-container">
                    <img
                        className="home-image"
                        src={iplLogo}
                        alt="iplLogo"
                    />
                </div>

                <nav className="header-nav">
                    <button className="nav-button" onClick={() => navigate("/dashboard")}>Dashboard</button>

                    <button className="nav-button" onClick={() => navigate("/documents")}>Documentos</button>
                </nav>
            </header>

            <main className="main-content">
                <Outlet />
            </main>
        </div>
    );
}