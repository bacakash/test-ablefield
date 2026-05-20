import React, { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

export default function CrmAgentDashboard() {
  const [customerId, setCustomerId] = useState(localStorage.getItem("crm_customer_id") || "");
  const [customer, setCustomer] = useState(null);
  const [conversation, setConversation] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [meta, setMeta] = useState("Intent, tags, and escalation details will appear here.");

  const [customerForm, setCustomerForm] = useState({
    full_name: "",
    email: "",
    company: "",
    phone: ""
  });

  const [message, setMessage] = useState("");
  const [channel, setChannel] = useState("chat");
  const [note, setNote] = useState("");
  const [ticket, setTicket] = useState({
    title: "",
    description: "",
    priority: "medium"
  });

  async function fetchAnalytics() {
    const res = await fetch(`${API}/analytics/summary`);
    setAnalytics(await res.json());
  }

  async function createCustomer() {
    const res = await fetch(`${API}/customers`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        ...customerForm,
        company: customerForm.company || null,
        phone: customerForm.phone || null
      })
    });
    const data = await res.json();
    setCustomer(data);
    setCustomerId(data.id);
    localStorage.setItem("crm_customer_id", data.id);
    fetchAnalytics();
  }

  async function useLastCustomer() {
    if (!customerId) return;
    const res = await fetch(`${API}/customers/${customerId}`);
    setCustomer(await res.json());
    loadConversation();
  }

  async function sendMessage() {
    if (!customerId) return;
    setConversation(prev => [...prev, {role: "customer", content: message}]);
    const res = await fetch(`${API}/conversations/${customerId}/message`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message, channel})
    });
    const data = await res.json();
    setConversation(prev => [...prev, {role: "agent", content: data.reply}]);
    setMeta(`Intent: ${data.detected_intent} | Sentiment: ${data.sentiment_score} | Escalate: ${data.should_escalate} | Tags: ${(data.suggested_tags || []).join(", ")}`);
    setMessage("");
    fetchAnalytics();
    useLastCustomer();
  }

  async function loadConversation() {
    if (!customerId) return;
    const res = await fetch(`${API}/conversations/${customerId}`);
    const data = await res.json();
    setConversation(data.messages || []);
  }

  async function createNote() {
    if (!customerId) return;
    await fetch(`${API}/customers/${customerId}/notes`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text: note})
    });
    setNote("");
  }

  async function createTicket() {
    if (!customerId) return;
    await fetch(`${API}/customers/${customerId}/tickets`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(ticket)
    });
    fetchAnalytics();
  }

  useEffect(() => {
    fetchAnalytics();
    if (customerId) useLastCustomer();
  }, []);

  return (
    <div style={{fontFamily: "Arial", background: "#f5f5f5", color: "#888", minHeight: "100vh"}}>
      <div style={{padding: 20, background: "#ededed", display: "flex", justifyContent: "space-between"}}>
        <div style={{fontSize: 28, fontWeight: "bold", color: "#b7b7b7"}}>NovaCRM // Agent Console</div>
        <div>
          <span onClick={fetchAnalytics} style={pill}>Analytics</span>
          <span onClick={() => setConversation([])} style={pill}>Clear</span>
          <span onClick={() => setMessage("I want pricing and a demo.")} style={pill}>Demo</span>
        </div>
      </div>

      <div style={{display: "grid", gridTemplateColumns: "340px 1fr 330px", gap: 18, padding: 18}}>
        <section style={card}>
          <div style={title}>Customer</div>
          <input style={field} placeholder="Full name" onChange={e => setCustomerForm({...customerForm, full_name: e.target.value})} />
          <input style={field} placeholder="Email" onChange={e => setCustomerForm({...customerForm, email: e.target.value})} />
          <input style={field} placeholder="Company" onChange={e => setCustomerForm({...customerForm, company: e.target.value})} />
          <input style={field} placeholder="Phone" onChange={e => setCustomerForm({...customerForm, phone: e.target.value})} />
          <button style={button} onClick={createCustomer}>Create</button>
          <div style={button} onClick={useLastCustomer}>Use last</div>

          <div style={box}>
            {customer ? (
              <>
                <b>{customer.full_name}</b><br />
                {customer.email}<br />
                ID: {customer.id}<br />
                Tags: {(customer.tags || []).join(", ")}
              </>
            ) : "No customer selected."}
          </div>

          <div style={title}>CRM Note</div>
          <textarea style={textarea} placeholder="Write a CRM note" value={note} onChange={e => setNote(e.target.value)} />
          <button style={button} onClick={createNote}>+</button>

          <div style={title}>Ticket</div>
          <input style={field} placeholder="Ticket title" onChange={e => setTicket({...ticket, title: e.target.value})} />
          <textarea style={textarea} placeholder="Ticket details" onChange={e => setTicket({...ticket, description: e.target.value})} />
          <select style={field} value={ticket.priority} onChange={e => setTicket({...ticket, priority: e.target.value})}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
          <button style={button} onClick={createTicket}>Create ticket</button>
        </section>

        <section style={card}>
          <div style={title}>Talk With AI Agent</div>
          <div style={chatBox}>
            {conversation.map((item, index) => (
              <div key={index} style={{...bubble, marginLeft: item.role === "agent" ? "auto" : 0}}>
                <b>{item.role}:</b> {item.content}
              </div>
            ))}
          </div>
          <textarea style={textarea} placeholder="Type customer message here..." value={message} onChange={e => setMessage(e.target.value)} />
          <select style={field} value={channel} onChange={e => setChannel(e.target.value)}>
            <option value="chat">Chat</option>
            <option value="email">Email</option>
            <option value="phone">Phone</option>
          </select>
          <button style={button} onClick={sendMessage}>Send</button>
          <button style={button} onClick={loadConversation}>Load conversation</button>
          <div style={box}>{meta}</div>
        </section>

        <section style={card}>
          <div style={title}>Analytics</div>
          <Metric label="Total customers" value={analytics?.total_customers ?? 0} />
          <Metric label="Total messages" value={analytics?.total_messages ?? 0} />
          <Metric label="Open tickets" value={analytics?.open_tickets ?? 0} />
          <Metric label="Avg sentiment" value={analytics?.average_sentiment ?? 0} />
          <Metric label="Escalation rate" value={`${analytics?.escalation_rate_percent ?? 0}%`} />
          <div style={title}>Top Intents</div>
          <TagList data={analytics?.top_intents || {}} />
          <div style={title}>Channels</div>
          <TagList data={analytics?.busiest_channels || {}} />
        </section>
      </div>
    </div>
  );
}

function Metric({label, value}) {
  return (
    <div style={{...box, marginBottom: 10}}>
      <div style={{fontSize: 30, fontWeight: "bold", color: "#c5c5c5"}}>{value}</div>
      <div>{label}</div>
    </div>
  );
}

function TagList({data}) {
  return (
    <div>
      {Object.entries(data).map(([key, value]) => (
        <span key={key} style={tag}>{key}: {String(value)}</span>
      ))}
    </div>
  );
}

const card = {
  background: "white",
  border: "1px solid #efefef",
  borderRadius: 18,
  padding: 18,
  boxShadow: "0 8px 22px rgba(0,0,0,.05)"
};
const field = {
  width: "100%",
  marginBottom: 10,
  border: "1px solid #eee",
  background: "#fafafa",
  color: "#b1b1b1",
  borderRadius: 12,
  padding: 12
};
const textarea = {...field, minHeight: 88};
const button = {
  border: 0,
  background: "#d7d7d7",
  color: "#fff",
  padding: "11px 15px",
  borderRadius: 14,
  cursor: "pointer",
  marginRight: 8,
  marginTop: 6,
  display: "inline-block"
};
const pill = {
  ...button,
  marginTop: 0
};
const title = {
  fontSize: 20,
  fontWeight: "bold",
  color: "#9e9e9e",
  marginTop: 18,
  marginBottom: 14
};
const box = {
  marginTop: 12,
  padding: 12,
  background: "#f3f3f3",
  borderRadius: 14,
  color: "#aaa",
  wordBreak: "break-word"
};
const chatBox = {
  height: 410,
  overflow: "auto",
  border: "1px solid #f0f0f0",
  background: "#fbfbfb",
  borderRadius: 18,
  padding: 14
};
const bubble = {
  maxWidth: "82%",
  padding: 12,
  margin: "10px 0",
  borderRadius: 18,
  color: "#a5a5a5",
  background: "#efefef"
};
const tag = {
  background: "#eeeeee",
  borderRadius: 999,
  display: "inline-block",
  padding: "6px 10px",
  margin: 4,
  fontSize: 12,
  color: "#b0b0b0"
};
