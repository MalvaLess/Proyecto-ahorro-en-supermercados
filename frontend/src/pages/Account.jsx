import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Account.css";
import { apiRequest } from "../services/apiClient";
import { getCurrentUser, logoutUser } from "../services/authService";

function Account() {
    const navigate = useNavigate();

    const [activeSection, setActiveSection] = useState("profile");

    const [formData, setFormData] = useState({
        firstName: "",
        lastName: "",
        email: "",
    });

    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [loadingUser, setLoadingUser] = useState(true);

    const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmNewPassword: "",
    });

    const [passwordMessage, setPasswordMessage] = useState("");
    const [passwordError, setPasswordError] = useState("");
    const [passwordLoading, setPasswordLoading] = useState(false);

  useEffect(() => {
    async function loadUserData() {
      try {
        const response = await apiRequest("/auth/me");

        const user = response.data;

        localStorage.setItem("user", JSON.stringify(user));

        setFormData({
          firstName: user.firstName || "",
          lastName: user.lastName || "",
          email: user.email || "",
        });
      } catch (error) {
        logoutUser();
        navigate("/login");
      } finally {
        setLoadingUser(false);
      }
    }

    const currentUser = getCurrentUser();

    if (currentUser) {
      setFormData({
        firstName: currentUser.firstName || "",
        lastName: currentUser.lastName || "",
        email: currentUser.email || "",
      });
    }

    loadUserData();
  }, [navigate]);

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData({
      ...formData,
      [name]: value,
    });
  }

  async function handleUpdateProfile(event) {
    event.preventDefault();

    try {
      setLoading(true);
      setError("");
      setMessage("");

      const currentUser = getCurrentUser();

      const response = await apiRequest(`/users/${currentUser.userId}`, {
        method: "PATCH",
        body: JSON.stringify({
          firstName: formData.firstName,
          lastName: formData.lastName,
          email: formData.email,
        }),
      });

      localStorage.setItem("user", JSON.stringify(response.data));

      setMessage("Perfil actualizado correctamente");
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

function handlePasswordChange(event) {
  const { name, value } = event.target;

  setPasswordData({
    ...passwordData,
    [name]: value,
  });
}

async function handleUpdatePassword(event) {
  event.preventDefault();

  const currentUser = getCurrentUser();

  if (!currentUser || !currentUser.userId) {
    setPasswordError("No se pudo identificar al usuario. Vuelve a iniciar sesión.");
    return;
  }

  if (passwordData.newPassword !== passwordData.confirmNewPassword) {
    setPasswordError("Las nuevas contraseñas no coinciden.");
    return;
  }

  if (passwordData.newPassword.length < 6) {
    setPasswordError("La nueva contraseña debe tener al menos 6 caracteres.");
    return;
  }

  try {
    setPasswordLoading(true);
    setPasswordError("");
    setPasswordMessage("");

    await apiRequest(`/users/${currentUser.userId}`, {
      method: "PATCH",
      body: JSON.stringify({
        currentPassword: passwordData.currentPassword,
        newPassword: passwordData.newPassword,
      }),
    });

    setPasswordData({
      currentPassword: "",
      newPassword: "",
      confirmNewPassword: "",
    });

    setPasswordMessage("Contraseña actualizada correctamente.");
  } catch (error) {
    setPasswordError(error.message);
  } finally {
    setPasswordLoading(false);
  }
}

function handleLogout() {
  logoutUser();
  navigate("/login");
}

  function renderContent() {
    if (activeSection === "profile") {
      return (
        <div className="account-content-card">
            <h2>Mi perfil</h2>
            <p>Actualiza tus datos personales.</p>

            {message && <p className="account-success">{message}</p>}
            {error && <p className="account-error">{error}</p>}

            {loadingUser ? (
                <p>Cargando datos del usuario...</p>
            ) : (
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
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        />
                    </div>

                    <button type="submit" disabled={loading}>
                        {loading ? "Guardando..." : "Guardar cambios"}
                    </button>
                </form>
            )}
        </div>
      );
    }

    if (activeSection === "change_password") {
      return (
        <div className="account-content-card">
            <h2>Cambiar contraseña</h2>
            <p>Actualiza tú contraseña de acceso.</p>

            {passwordMessage && <p className="account-success">{passwordMessage}</p>}
            {passwordError && <p className="account-error">{passwordError}</p>}

            <form className="account-form" onSubmit={handleUpdatePassword}>
                <div className="input-group">
                <label>Contraseña actual</label>
                <input
                    type="password"
                    name="currentPassword"
                    value={passwordData.currentPassword}
                    onChange={handlePasswordChange}
                    placeholder="Ingresa tu contraseña actual"
                />
                </div>

                <div className="input-group">
                <label>Nueva contraseña</label>
                <input
                    type="password"
                    name="newPassword"
                    value={passwordData.newPassword}
                    onChange={handlePasswordChange}
                    placeholder="Ingresa tu nueva contraseña"
                />
                </div>

                <div className="input-group">
                <label>Confirmar nueva contraseña</label>
                <input
                    type="password"
                    name="confirmNewPassword"
                    value={passwordData.confirmNewPassword}
                    onChange={handlePasswordChange}
                    placeholder="Confirma tu nueva contraseña"
                />
                </div>

                <button type="submit" disabled={passwordLoading}>
                {passwordLoading ? "Actualizando..." : "Actualizar contraseña"}
                </button>
            </form>
        </div>
      );
    }

    if (activeSection === "shoppingLists") {
      return (
        <div className="account-content-card">
          <h2>Mis compras</h2>
          <p>Aquí mostraremos las listas de compras del usuario.</p>
        </div>
      );
    }

    if (activeSection === "favorites") {
      return (
        <div className="account-content-card">
          <h2>Mis favoritos</h2>
          <p>Aquí mostraremos los productos favoritos del usuario.</p>
        </div>
      );
    }

    return null;
  }

  return (
    <section className="account-page">
      <aside className="account-sidebar">
        <h1>Mi cuenta</h1>

        <button
            className={activeSection === "profile" ? "active" : ""}
            onClick={() => setActiveSection("profile")}
        >
          Mi perfil
        </button>

        <button
            className={activeSection === "change_password" ? "active" : ""}
            onClick={() => setActiveSection("change_password")}
        >
          Cambiar contraseña
        </button>

        <button
            className={activeSection === "shoppingLists" ? "active" : ""}
            onClick={() => setActiveSection("shoppingLists")}
        >
          Mis compras
        </button>

        <button
            className={activeSection === "favorites" ? "active" : ""}
            onClick={() => setActiveSection("favorites")}
        >
          Mis favoritos
        </button>

        <button
            type="button"
            className="logout-account-button"
            onClick={handleLogout}
        >
          Cerrar sesión
        </button>
      </aside>

      <main className="account-content">{renderContent()}</main>
    </section>
  );
}

export default Account;