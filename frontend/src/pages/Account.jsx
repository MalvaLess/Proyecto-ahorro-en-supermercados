import { useState } from "react";
import { apiRequest } from "../services/apiClient";
import { getCurrentUser } from "../services/authService";
import "./Account.css";

function Account() {
    const currentUser = getCurrentUser();

    const [ activeSection, setActiveSection ] = useState("profile");
    const [ formData, setFormData ] = useState({
        firstName: currentUser?.firstName || "",
        lastName: currentUser?.lastName || "",
        email: currentUser?.email || "",
    });

    const [ message, setMessage ] = useState("");
    const [ error, setError ] = useState("");
    const [ loading, setLoading ] = useState(false);

    function handleChange(event) {
        const { name, value } = event.target;

        setFormData({
            ...formData,
            [name]: value
        });
    }

    async function handleUpdateProfile(event) {
        event.preventDefault();

        try {
            setLoading(true);
            setError("");
            setMessage("");

            const response = await apiRequest(`/users/${currentUser.userId}`, {
                method: "PUT",
                body: JSON.stringify({
                    firstName: formData.firstName,
                    lastName: formData.lastName,
                    email: formData.email
                })
            });

            localStorage.setItem("user", JSON.stringify(response.data));

            setMessage("Perfil actualizado correctamente");
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    }

    function renderContent() {
        if (activeSection === "profile") {
            return (
                <div className="account-content-card">
                    <h2>Mi Perfil</h2>
                    <p>Actualiza tus datos personales.</p>

                    {message && <p className="account-success">{message}</p>}
                    {error && <p className="account-error">{error}</p>}

                    <form className="account-form" onSubmit={handleUpdateProfile}>
                        <div className="input-group">
                            <label>Nombre</label>
                            <input 
                            type="text"
                            name="firstName"
                            value={formData.firstName}
                            onChange={handleChange}
                            />
                        </div>

                        <div className="input-group">
                            <label>Apellido</label>
                            <input 
                            type="text"
                            name="lastName"
                            value={formData.lastName}
                            onChange={handleChange}
                            />
                        </div>

                        <div className="input-group">
                            <label>Correo electrónico</label>
                            <input 
                            type="text"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            />
                        </div>

                        <button type="submit" disabled={loading}>
                            {loading ? "Guardando..." : "Guardar Cambios"}
                        </button>
                    </form>
                </div>
            );
        }

        if (activeSection === "shoppingLists") {
            return (
                <div className="account-content-card">
                    <h2>Mis Compras</h2>
                    <p>Mis Compras</p>
                </div>
            );
        }

        if (activeSection === "favorites") {
            return (
                <div className="account-content-card">
                    <h2>Mis Favoritos</h2>
                    <p>Mis Favoritos</p>
                </div>
            );
        }

        return null;
    }

    return (
        <section className="account-page">
            <aside className="account-sidebar">
                <h1>Mi Cuenta</h1>

                <button 
                    className={activeSection === "profile" ? "active" : ""}
                    onClick={() => setActiveSection("profile")}
                    >
                    Mi Perfil
                </button>

                <button 
                    className={activeSection === "shoppingLists" ? "active" : ""}
                    onClick={() => setActiveSection("shoppingLists")}
                    >
                    Mis Compras
                </button>

                <button 
                    className={activeSection === "favorites" ? "active" : ""}
                    onClick={() => setActiveSection("favorites")}
                    >
                    Mis Favoritos
                </button>
            </aside>

            <main className="account-content">
                {renderContent()}
            </main>
        </section>
    )
}

export default Account;