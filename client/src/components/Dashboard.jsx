import { useState, useEffect } from "react";
import { API_BASE_URL } from "../config/api";
import "./Dashboard.css";

function Dashboard({ token, onLogout }) {
  const [forms, setForms] = useState([]);
  const [title, setTitle] = useState("");
  const [respondents, setRespondents] = useState([{ name: "", email: "" }]);

  // 載入現有表單
  useEffect(() => {
    const fetchForms = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/forms`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (res.ok) {
          const data = await res.json();
          setForms(data);
        }
      } catch (error) {
        console.error("載入表單失敗:", error);
      }
    };

    if (token) {
      fetchForms();
    }
  }, [token]);

  const createForm = async () => {
    const body = {
      title,
      respondents,
    };
    const res = await fetch(`${API_BASE_URL}/forms`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    });
    if (res.ok) {
      const data = await res.json();
      setForms([...forms, data]);
      setTitle("");
      setRespondents([{ name: "", email: "" }]);
    } else {
      alert("建立失敗");
    }
  };

  const addRespondent = () => {
    setRespondents([...respondents, { name: "", email: "" }]);
  };

  const updateRespondent = (index, field, value) => {
    const next = respondents.slice();
    next[index][field] = value;
    setRespondents(next);
  };

  const removeRespondent = (index) => {
    if (respondents.length > 1) {
      setRespondents(respondents.filter((_, i) => i !== index));
    }
  };

  const inviteLink = (form) =>
    `${window.location.origin}?code=${form.invite_code}`;

  const generateResults = async (formId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/forms/${formId}/results`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.ok) {
        const results = await res.json();
        // 顯示結果摘要
        const summary = `
表單結果摘要：
• 表單名稱：${results.title}
• 總受邀者：${results.total_respondents} 人
• 已回覆：${results.total_responses} 人
• 回覆率：${results.response_rate}

回饋內容：
${results.responses.map((r, i) => `${i + 1}. ${r.feedback_content}`).join("\n")}
        `;

        // 使用更友好的方式顯示結果
        if (confirm(`${summary}\n\n是否要在新視窗中查看詳細結果？`)) {
          // 未來可以導航到專門的結果頁面
          console.log("完整結果數據:", results);
        }
      } else {
        const error = await res.json();
        alert(`生成結果失敗: ${error.message || "未知錯誤"}`);
      }
    } catch (error) {
      console.error("生成結果時發生錯誤:", error);
      alert("生成結果時發生錯誤，請檢查網路連線");
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>表單管理</h2>
        <button onClick={onLogout} className="logout-btn">
          登出
        </button>
      </div>

      <div className="create-form-section">
        <h3>建立表單</h3>
        <div className="form-group">
          <input
            placeholder="表單名稱"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <h4>受邀者</h4>
        <div className="respondents-list">
          {respondents.map((r, i) => (
            <div key={i} className="respondent-item">
              <input
                placeholder="姓名"
                value={r.name}
                onChange={(e) => updateRespondent(i, "name", e.target.value)}
              />
              <input
                placeholder="Email"
                value={r.email}
                onChange={(e) => updateRespondent(i, "email", e.target.value)}
                type="email"
              />
              {respondents.length > 1 && (
                <button
                  onClick={() => removeRespondent(i)}
                  className="remove-btn"
                >
                  移除
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="form-actions">
          <button onClick={addRespondent}>新增受邀者</button>
          <button onClick={createForm} className="create-btn">
            建立表單
          </button>
        </div>
      </div>

      <div className="forms-list-section">
        <h3>已建立表單</h3>
        {forms.length === 0 ? (
          <p>尚未建立任何表單</p>
        ) : (
          <ul className="forms-list">
            {forms.map((f) => (
              <li key={f.form_id} className="form-item">
                <div className="form-info">
                  <strong>{f.title}</strong>
                  <span>邀請碼: {f.invite_code}</span>
                </div>
                <div className="form-actions-buttons">
                  <a
                    href={inviteLink(f)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="fill-link"
                  >
                    填寫連結
                  </a>
                  <button
                    onClick={() => generateResults(f.form_id)}
                    className="generate-results-btn"
                  >
                    產生結果
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
