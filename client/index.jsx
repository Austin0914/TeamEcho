const API = 'http://localhost:8000';

function App() {
  const [token, setToken] = React.useState(localStorage.getItem('token'));
  const [view, setView] = React.useState(token ? 'dashboard' : 'login');

  const handleLogin = async (email, password) => {
    const res = await fetch(`${API}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      setView('dashboard');
    } else {
      alert('登入失敗');
    }
  };

  const handleRegister = async (name, email, password) => {
    const res = await fetch(`${API}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    if (res.ok) {
      alert('註冊成功，請登入');
      setView('login');
    } else {
      alert('註冊失敗');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setView('login');
  };

  switch (view) {
    case 'login':
      return <Login onLogin={handleLogin} onSwitch={() => setView('register')} />;
    case 'register':
      return <Register onRegister={handleRegister} onSwitch={() => setView('login')} />;
    case 'dashboard':
      return <Dashboard token={token} onLogout={handleLogout} />;
    default:
      return null;
  }
}

function Login({ onLogin, onSwitch }) {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  return (
    <div>
      <h2>登入</h2>
      <div><input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} /></div>
      <div><input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} /></div>
      <button onClick={() => onLogin(email, password)}>登入</button>
      <div>沒有帳號？ <a href="#" onClick={e => {e.preventDefault(); onSwitch();}}>註冊</a></div>
    </div>
  );
}

function Register({ onRegister, onSwitch }) {
  const [name, setName] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  return (
    <div>
      <h2>註冊</h2>
      <div><input placeholder="Name" value={name} onChange={e => setName(e.target.value)} /></div>
      <div><input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} /></div>
      <div><input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} /></div>
      <button onClick={() => onRegister(name, email, password)}>註冊</button>
      <div>已有帳號？ <a href="#" onClick={e => {e.preventDefault(); onSwitch();}}>登入</a></div>
    </div>
  );
}

function Dashboard({ token, onLogout }) {
  const [forms, setForms] = React.useState([]);
  const [title, setTitle] = React.useState('');
  const [respondents, setRespondents] = React.useState([{ name: '', email: '' }]);

  const fetchForms = async () => {
    // simple listing of responses for each form
    // For demo, we don't have list forms API, so keep local only
  };

  const createForm = async () => {
    const body = {
      title,
      respondents
    };
    const res = await fetch(`${API}/forms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(body)
    });
    if (res.ok) {
      const data = await res.json();
      setForms([...forms, data]);
      setTitle('');
      setRespondents([{ name: '', email: '' }]);
    } else {
      alert('建立失敗');
    }
  };

  const addRespondent = () => {
    setRespondents([...respondents, { name: '', email: '' }]);
  };

  const updateRespondent = (index, field, value) => {
    const next = respondents.slice();
    next[index][field] = value;
    setRespondents(next);
  };

  const inviteLink = form => `${window.location.origin}/fill.html?code=${form.invite_code}`;

  return (
    <div>
      <h2>表單管理</h2>
      <button onClick={onLogout}>登出</button>
      <h3>建立表單</h3>
      <div>
        <input placeholder="表單名稱" value={title} onChange={e => setTitle(e.target.value)} />
      </div>
      <h4>受邀者</h4>
      {respondents.map((r, i) => (
        <div key={i}>
          <input placeholder="姓名" value={r.name} onChange={e => updateRespondent(i, 'name', e.target.value)} />
          <input placeholder="Email" value={r.email} onChange={e => updateRespondent(i, 'email', e.target.value)} />
        </div>
      ))}
      <button onClick={addRespondent}>新增受邀者</button>
      <div><button onClick={createForm}>建立</button></div>

      <h3>已建立表單</h3>
      <ul>
        {forms.map(f => (
          <li key={f.form_id}>
            {f.title} - 邀請碼 {f.invite_code} - <a href={inviteLink(f)} target="_blank">填寫連結</a>
          </li>
        ))}
      </ul>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
