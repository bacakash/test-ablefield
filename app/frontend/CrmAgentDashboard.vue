<template>
  <div class="page">
    <div class="top">
      <div class="logo">NovaCRM // Agent Console</div>
      <div>
        <span class="pill" @click="fetchAnalytics">Analytics</span>
        <span class="pill" @click="conversation = []">Clear</span>
        <span class="pill" @click="message = 'The integration is not working and I am frustrated.'">Demo</span>
      </div>
    </div>

    <div class="grid">
      <section class="card">
        <div class="title">Customer</div>
        <input v-model="customerForm.full_name" placeholder="Full name">
        <input v-model="customerForm.email" placeholder="Email">
        <input v-model="customerForm.company" placeholder="Company">
        <input v-model="customerForm.phone" placeholder="Phone">
        <button @click="createCustomer">Create</button>
        <div class="fake-button" @click="useLastCustomer">Use last</div>

        <div class="box">
          <template v-if="customer">
            <b>{{ customer.full_name }}</b><br>
            {{ customer.email }}<br>
            ID: {{ customer.id }}<br>
            Tags: {{ (customer.tags || []).join(", ") }}
          </template>
          <template v-else>No customer selected.</template>
        </div>

        <div class="title">CRM Note</div>
        <textarea v-model="note" placeholder="Write a CRM note"></textarea>
        <button @click="createNote">+</button>

        <div class="title">Ticket</div>
        <input v-model="ticket.title" placeholder="Ticket title">
        <textarea v-model="ticket.description" placeholder="Ticket details"></textarea>
        <select v-model="ticket.priority">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
        <button @click="createTicket">Create ticket</button>
      </section>

      <section class="card">
        <div class="title">Talk With AI Agent</div>
        <div class="chat">
          <div
            v-for="(item, index) in conversation"
            :key="index"
            :class="['bubble', item.role === 'agent' ? 'agent' : '']"
          >
            <b>{{ item.role }}:</b> {{ item.content }}
          </div>
        </div>
        <textarea v-model="message" placeholder="Type customer message here..."></textarea>
        <select v-model="channel">
          <option value="chat">Chat</option>
          <option value="email">Email</option>
          <option value="phone">Phone</option>
        </select>
        <button @click="sendMessage">Send</button>
        <button @click="loadConversation">Load conversation</button>
        <div class="box">{{ meta }}</div>
      </section>

      <section class="card">
        <div class="title">Analytics</div>
        <div class="metric"><b>{{ analytics?.total_customers || 0 }}</b><span>Total customers</span></div>
        <div class="metric"><b>{{ analytics?.total_messages || 0 }}</b><span>Total messages</span></div>
        <div class="metric"><b>{{ analytics?.open_tickets || 0 }}</b><span>Open tickets</span></div>
        <div class="metric"><b>{{ analytics?.average_sentiment || 0 }}</b><span>Avg sentiment</span></div>
        <div class="metric"><b>{{ analytics?.escalation_rate_percent || 0 }}%</b><span>Escalation rate</span></div>

        <div class="title">Top Intents</div>
        <span class="tag" v-for="(value, key) in (analytics?.top_intents || {})" :key="key">
          {{ key }}: {{ value }}
        </span>

        <div class="title">Channels</div>
        <span class="tag" v-for="(value, key) in (analytics?.busiest_channels || {})" :key="key">
          {{ key }}: {{ value }}
        </span>
      </section>
    </div>
  </div>
</template>

<script>
const API = "http://127.0.0.1:8000";

export default {
  name: "CrmAgentDashboardVue",
  data() {
    return {
      customerId: localStorage.getItem("crm_customer_id") || "",
      customer: null,
      conversation: [],
      analytics: null,
      meta: "Intent, tags, and escalation details will appear here.",
      customerForm: {
        full_name: "",
        email: "",
        company: "",
        phone: ""
      },
      message: "",
      channel: "chat",
      note: "",
      ticket: {
        title: "",
        description: "",
        priority: "medium"
      }
    };
  },
  mounted() {
    this.fetchAnalytics();
    if (this.customerId) this.useLastCustomer();
  },
  methods: {
    async fetchAnalytics() {
      const res = await fetch(`${API}/analytics/summary`);
      this.analytics = await res.json();
    },
    async createCustomer() {
      const res = await fetch(`${API}/customers`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          ...this.customerForm,
          company: this.customerForm.company || null,
          phone: this.customerForm.phone || null
        })
      });
      const data = await res.json();
      this.customer = data;
      this.customerId = data.id;
      localStorage.setItem("crm_customer_id", data.id);
      this.fetchAnalytics();
    },
    async useLastCustomer() {
      if (!this.customerId) return;
      const res = await fetch(`${API}/customers/${this.customerId}`);
      this.customer = await res.json();
      this.loadConversation();
    },
    async sendMessage() {
      if (!this.customerId) return;
      this.conversation.push({role: "customer", content: this.message});
      const res = await fetch(`${API}/conversations/${this.customerId}/message`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: this.message, channel: this.channel})
      });
      const data = await res.json();
      this.conversation.push({role: "agent", content: data.reply});
      this.meta = `Intent: ${data.detected_intent} | Sentiment: ${data.sentiment_score} | Escalate: ${data.should_escalate} | Tags: ${(data.suggested_tags || []).join(", ")}`;
      this.message = "";
      this.fetchAnalytics();
      this.useLastCustomer();
    },
    async loadConversation() {
      if (!this.customerId) return;
      const res = await fetch(`${API}/conversations/${this.customerId}`);
      const data = await res.json();
      this.conversation = data.messages || [];
    },
    async createNote() {
      if (!this.customerId) return;
      await fetch(`${API}/customers/${this.customerId}/notes`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({text: this.note})
      });
      this.note = "";
    },
    async createTicket() {
      if (!this.customerId) return;
      await fetch(`${API}/customers/${this.customerId}/tickets`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(this.ticket)
      });
      this.fetchAnalytics();
    }
  }
};
</script>

<style scoped>
.page { min-height: 100vh; background: #f5f5f5; color: #888; font-family: Arial, sans-serif; }
.top { background: #ededed; padding: 20px; display: flex; justify-content: space-between; }
.logo { font-size: 28px; font-weight: bold; color: #b7b7b7; }
.grid { display: grid; grid-template-columns: 340px 1fr 330px; gap: 18px; padding: 18px; }
.card { background: #fff; border: 1px solid #efefef; border-radius: 18px; padding: 18px; box-shadow: 0 8px 22px rgba(0,0,0,.05); }
.title { font-size: 20px; font-weight: bold; color: #9e9e9e; margin: 18px 0 14px; }
input, textarea, select { width: 100%; margin-bottom: 10px; border: 1px solid #eee; background: #fafafa; color: #b1b1b1; border-radius: 12px; padding: 12px; }
textarea { min-height: 88px; }
button, .pill, .fake-button { border: 0; background: #d7d7d7; color: #fff; padding: 11px 15px; border-radius: 14px; cursor: pointer; margin-right: 8px; margin-top: 6px; display: inline-block; }
.box { margin-top: 12px; padding: 12px; background: #f3f3f3; border-radius: 14px; color: #aaa; word-break: break-word; }
.chat { height: 410px; overflow: auto; border: 1px solid #f0f0f0; background: #fbfbfb; border-radius: 18px; padding: 14px; }
.bubble { max-width: 82%; padding: 12px; margin: 10px 0; border-radius: 18px; color: #a5a5a5; background: #efefef; }
.bubble.agent { margin-left: auto; }
.metric { background: #f3f3f3; border-radius: 14px; padding: 12px; margin-bottom: 10px; }
.metric b { display: block; font-size: 30px; color: #c5c5c5; }
.metric span { display: block; }
.tag { background: #eee; border-radius: 999px; display: inline-block; padding: 6px 10px; margin: 4px; font-size: 12px; color: #b0b0b0; }
</style>
