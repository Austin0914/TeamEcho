import { useState, useEffect } from "react";
import Login from "./components/Login";
import Register from "./components/Register";
import Dashboard from "./components/Dashboard";
import FillForm from "./components/FillForm";
import { API_BASE_URL } from "./config/api";
import "./styles/base.css";
import "./App.css";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [view, setView] = useState(() => {
    // 檢查 URL 參數來決定初始視圖
    const urlParams = new URLSearchParams(window.location.search);
    const inviteCode = urlParams.get("code");
    if (inviteCode) {
      return "fill";
    }
    return token ? "dashboard" : "login";
  });

  const handleLogin = async (email, password) => {
    const res = await fetch(`${API_BASE_URL}/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);
      setView("dashboard");
    } else {
      alert("登入失敗");
    }
  };

  const handleRegister = async (name, email, password) => {
    const res = await fetch(`${API_BASE_URL}/users`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });
    if (res.ok) {
      alert("註冊成功，請登入");
      setView("login");
    } else {
      alert("註冊失敗");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setView("login");
  };

  const handleCodeEntry = (code) => {
    // 使用邀請碼進入填寫頁面
    window.history.pushState({}, "", `?code=${code}`);
    setView("fill");
  };

  switch (view) {
    case "login":
      return (
        <div className="auth-page">
          <Login
            onLogin={handleLogin}
            onSwitch={() => setView("register")}
            onCodeEntry={handleCodeEntry}
          />
        </div>
      );
    case "register":
      return (
        <div className="auth-page">
          <Register
            onRegister={handleRegister}
            onSwitch={() => setView("login")}
            onCodeEntry={handleCodeEntry}
          />
        </div>
      );
    case "dashboard":
      return (
        <div className="dashboard-page">
          <Dashboard token={token} onLogout={handleLogout} />
        </div>
      );
    case "fill":
      return (
        <div className="dashboard-page">
          <FillForm onBack={() => setView("login")} />
        </div>
      );
    default:
      return null;
  }
}

export default App;
