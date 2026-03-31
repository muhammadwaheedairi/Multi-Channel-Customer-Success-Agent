export type Category = "general" | "technical" | "billing" | "feedback" | "bug_report"
export type Priority = "low" | "medium" | "high"
export type TicketStatus = "open" | "in_progress" | "resolved" | "escalated"
export type Channel = "web_form" | "email" | "whatsapp"

export interface SubmitFormResponse {
  ticket_id: string
  message: string
  estimated_response_time: string
}

export interface Message {
  role: "customer" | "agent" | "system"
  content: string
  channel: Channel
  created_at: string
}

export interface TicketMessagesResponse {
  ticket_id: string
  messages: Message[]
}

export interface MetricsSummary {
  total_tickets: number
  open_tickets: number
  resolved_tickets: number
  total_customers: number
}

export interface ChannelMetric {
  total_conversations: number
  escalations: number
  avg_sentiment: number | null
}
