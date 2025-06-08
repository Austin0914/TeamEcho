import { useState } from "react";
import "./Login.css";

function Login({ onLogin, onSwitch, onCodeEntry }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [inviteCode, setInviteCode] = useState("");

  const handleCodeSubmit = () => {
    if (inviteCode.trim()) {
      onCodeEntry(inviteCode.trim());
    } else {
      alert("請輸入邀請碼");
    }
  };

  return (
    <div className="auth-wrapper">
      <h1 className="app-title">TeamEcho</h1>
      <div className="auth-main">
        <div className="auth-container">
          <div className="auth-content">
            <div className="auth-form-section">
              <h2>登入</h2>
              <div className="form-group">
                <input
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  type="email"
                />
              </div>
              <div className="form-group">
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>
            <div className="auth-button-section">
              <button onClick={() => onLogin(email, password)}>登入</button>
              <div className="switch-auth">
                沒有帳號？
                <a
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    onSwitch();
                  }}
                >
                  註冊
                </a>
              </div>
            </div>
          </div>
        </div>

        <div className="divider">或</div>

        <div className="code-entry-container">
          <div className="code-entry-content">
            <h3>使用邀請碼</h3>
            <div className="form-group">
              <input
                placeholder="請輸入邀請碼"
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value)}
              />
            </div>
            <button onClick={handleCodeSubmit} className="submit-btn">
              直接填寫表單
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
