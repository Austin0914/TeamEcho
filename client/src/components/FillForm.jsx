import { useState, useEffect } from "react";
import { API_BASE_URL } from "../config/api";
import "./FillForm.css";

function FillForm({ onBack }) {
  const [form, setForm] = useState(null);
  const [feedbacks, setFeedbacks] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const urlParams = new URLSearchParams(window.location.search);
  const inviteCode = urlParams.get("code");

  useEffect(() => {
    if (!inviteCode) {
      setError("缺少邀請碼");
      setLoading(false);
      return;
    }

    fetch(`${API_BASE_URL}/invite/${inviteCode}`)
      .then((r) => (r.ok ? r.json() : Promise.reject("邀請碼無效")))
      .then((data) => {
        setForm(data);
        // 初始化每個受邀者的回饋內容為空字符串
        const initialFeedbacks = {};
        if (data.respondents) {
          data.respondents.forEach((respondent) => {
            initialFeedbacks[respondent.email] = "";
          });
        }
        setFeedbacks(initialFeedbacks);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  }, [inviteCode]);

  const updateFeedback = (email, content) => {
    setFeedbacks((prev) => ({
      ...prev,
      [email]: content,
    }));
  };

  const submit = async () => {
    // 檢查是否至少有一個回饋內容
    const hasContent = Object.values(feedbacks).some((content) =>
      content.trim()
    );
    if (!hasContent) {
      alert("請至少為一位受邀者填寫回饋內容");
      return;
    }

    setSubmitting(true);

    try {
      // 為每個有內容的受邀者提交回饋
      const submissions = Object.entries(feedbacks)
        .filter(([email, content]) => content.trim())
        .map(([email, content]) =>
          fetch(`${API_BASE_URL}/invite/${inviteCode}/responses`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              respondent_email: email,
              feedback_content: content.trim(),
            }),
          })
        );

      const results = await Promise.all(submissions);
      const allSuccessful = results.every((res) => res.ok);

      if (allSuccessful) {
        alert("感謝填寫！所有回饋已成功提交");
        // 清空所有回饋內容
        const clearedFeedbacks = {};
        Object.keys(feedbacks).forEach((email) => {
          clearedFeedbacks[email] = "";
        });
        setFeedbacks(clearedFeedbacks);
      } else {
        alert("部分回饋提交失敗，請重試");
      }
    } catch (error) {
      alert("提交失敗，請檢查網路連線");
    } finally {
      setSubmitting(false);
    }
  };

  const handleBack = () => {
    // 清除 URL 參數
    window.history.pushState({}, "", window.location.pathname);
    onBack();
  };

  if (loading) return <div className="loading">載入中...</div>;

  if (error) {
    return (
      <div className="fill-form-wrapper">
        <h1 className="app-title">TeamEcho</h1>
        <div className="auth-container">
          <div className="error" style={{ marginBottom: "1rem" }}>
            錯誤: {error}
          </div>
          <button onClick={handleBack} style={{ width: "100%" }}>
            返回首頁
          </button>
        </div>
      </div>
    );
  }

  if (!form) {
    return (
      <div className="fill-form-wrapper">
        <h1 className="app-title">TeamEcho</h1>
        <div className="auth-container">
          <div className="error" style={{ marginBottom: "1rem" }}>
            表單不存在
          </div>
          <button onClick={handleBack} style={{ width: "100%" }}>
            返回首頁
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fill-form-wrapper">
      <h1 className="app-title">TeamEcho</h1>
      <div className="fill-form-container">
        <div className="form-header">
          <h2>{form.title}</h2>
          <p className="form-description">請為以下人員提供回饋意見</p>
        </div>

        <div className="respondents-feedback-list">
          {form.respondents &&
            form.respondents.map((respondent) => (
              <div key={respondent.email} className="respondent-feedback-item">
                <div className="respondent-info">
                  <h3>{respondent.name}</h3>
                </div>
                <div className="feedback-input-section">
                  <textarea
                    rows="6"
                    placeholder={`請輸入對 ${respondent.name} 的回饋...`}
                    value={feedbacks[respondent.email] || ""}
                    onChange={(e) =>
                      updateFeedback(respondent.email, e.target.value)
                    }
                    className="feedback-textarea"
                  />
                </div>
              </div>
            ))}
        </div>

        <div className="form-actions">
          <button onClick={submit} disabled={submitting} className="submit-btn">
            {submitting ? "提交中..." : "送出所有回饋"}
          </button>
          <div style={{ textAlign: "center", marginTop: "1rem" }}>
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                handleBack();
              }}
              style={{ color: "#6c757d", textDecoration: "none" }}
            >
              返回首頁
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FillForm;
