const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function submitSupportForm(data: {
  name: string
  email: string
  subject: string
  category: string
  priority: string
  message: string
}) {
  const res = await fetch(`${API_URL}/support/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || "Submission failed")
  }
  return res.json()
}

export async function getTicketMessages(ticketId: string) {
  const res = await fetch(`${API_URL}/support/ticket/${ticketId}/messages`)
  if (!res.ok) throw new Error("Ticket not found")
  return res.json()
}

export async function getTicketStatus(ticketId: string) {
  const res = await fetch(`${API_URL}/support/ticket/${ticketId}`)
  if (!res.ok) throw new Error("Ticket not found")
  return res.json()
}

export async function getMetricsSummary() {
  const res = await fetch(`${API_URL}/metrics/summary`)
  if (!res.ok) throw new Error("Failed to fetch metrics")
  return res.json()
}

export async function getChannelMetrics() {
  const res = await fetch(`${API_URL}/metrics/channels`)
  if (!res.ok) throw new Error("Failed to fetch channel metrics")
  return res.json()
}
