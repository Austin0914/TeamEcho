const API = 'http://localhost:8000';
const urlParams = new URLSearchParams(window.location.search);
const inviteCode = urlParams.get('code');

function App() {
  const [form, setForm] = React.useState(null);
  const [content, setContent] = React.useState('');

  React.useEffect(() => {
    fetch(`${API}/invite/${inviteCode}`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(setForm)
      .catch(() => alert('邀請碼無效'));
  }, []);

  const submit = async () => {
    const res = await fetch(`${API}/invite/${inviteCode}/responses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback_content: content })
    });
    if (res.ok) {
      alert('感謝填寫');
      setContent('');
    } else {
      alert('提交失敗');
    }
  };

  if (!form) return null;

  return (
    <div>
      <h2>{form.title}</h2>
      <textarea rows="5" cols="60" value={content} onChange={e => setContent(e.target.value)} />
      <div><button onClick={submit}>送出</button></div>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
