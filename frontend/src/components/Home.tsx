import { useNavigate } from "react-router";

export function Home() {
    const navigate = useNavigate();

    return (
        <div className="home-container">
            <button onClick={() => navigate("/dashboard")}>Dashboard</button>
            <button onClick={() => navigate("/documents")}>SearchBar</button>
        </div>
    );
}