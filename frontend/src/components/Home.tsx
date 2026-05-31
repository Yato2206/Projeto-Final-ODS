import React from "react"
import { useNavigate, Outlet } from "react-router"

export function Home() {
    const navigate = useNavigate();

    return (
        <div>
        <div className="home-container">
            <button onClick={() => navigate("/dashboard")}>Dashboard</button>
            <button onClick={() => navigate("/documents")}>Documents</button>
        </div>

            <Outlet />
        </div>
    );
}