import { useState } from "react";
import "./Register.css";

function Register({ onRegister, onSwitch, onCodeEntry }) {
  const [name, setName] = useState("");
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
        {/* 註冊表單容器 */}
        <div className="auth-container">
          <div className="auth-content">
            <div className="auth-form-section">
              <h2>註冊</h2>
              <div className="form-group">
                <input
                  placeholder="Name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
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
              <button onClick={() => onRegister(name, email, password)}>
                註冊
              </button>
              <div className="switch-auth">
                已有帳號？
                <a
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    onSwitch();
                  }}
                >
                  登入
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* 分隔符 */}
        <div className="divider">或</div>

        {/* 邀請碼輸入容器 */}
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

export default Register;
