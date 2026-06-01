import { apiRequest } from "./apiClient";

export async function loginUser(credentials) {
    const response = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify(credentials),
    });

    const { access_token, token_type, expiresIn, user } = response.data;

    localStorage.setItem("access_token", access_token);
    localStorage.setItem("token_type", token_type);
    localStorage.setItem("expiresIn", expiresIn);
    localStorage.setItem("user", JSON.stringify(user));

    window.dispatchEvent(new Event("auth-change"));

    return response.data;
}

export async function registerUser(userData) {
    const response = await apiRequest("/users", {
        method: "POST",
        body: JSON.stringify(userData)
    })

    return response.data;
}

export function logoutUser() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("token_type");
  localStorage.removeItem("expiresIn");
  localStorage.removeItem("user");

  window.dispatchEvent(new Event("auth-change"));
}

export function getCurrentUser() {
    const user = localStorage.getItem("user");

    if (!user) {
        return null;
    }

    return JSON.parse(user);
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem("access_token"));
}