"use client"

import { useEffect, useState } from "react"
import { getTicketStatus, getTicketMessages } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

const STATUS_COLOR: Record<string, string> = {
  open: "bg-blue-100 text-blue-700",
  in_progress: "bg-yellow-100 text-yellow-700",
  resolved: "bg-green-100 text-green-700",
  escalated: "bg-red-100 text-red-700",
}

export default function TicketPage({ params }: { params: Promise<{ id: string }> }) {
  const [ticketId, setTicketId] = useState("")
  const [ticket, setTicket] = useState<any>(null)
  const [messages, setMessages] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    params.then(p => setTicketId(p.id))
  }, [params])

  useEffect(() => {
    if (!ticketId) return
    const fetchData = async () => {
      try {
        const [t, m] = await Promise.all([
          getTicketStatus(ticketId),
          getTicketMessages(ticketId)
        ])
        setTicket(t)
        setMessages(m.messages || [])
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [ticketId])

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-muted-foreground">Loading ticket...</p>
    </div>
  )

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-2xl mx-auto space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Ticket Status</h1>
          <a href="/support"><Button variant="outline" size="sm">New Request</Button></a>
        </div>

        {ticket && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-mono text-muted-foreground">{ticketId}</CardTitle>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${STATUS_COLOR[ticket.status] || ""}`}>
                  {ticket.status.replace("_", " ").toUpperCase()}
                </span>
              </div>
              <div className="flex gap-2 mt-2">
                <Badge variant="outline">{ticket.channel}</Badge>
                <Badge variant="outline">{ticket.category}</Badge>
                <Badge variant="outline">{ticket.priority}</Badge>
              </div>
            </CardHeader>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Conversation</CardTitle>
            <CardDescription>Auto-refreshes every 5 seconds</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {messages.length === 0 ? (
              <p className="text-muted-foreground text-sm">Agent is processing your request...</p>
            ) : (
              messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "agent" ? "justify-start" : "justify-end"}`}>
                  <div className={`max-w-[80%] rounded-lg p-3 text-sm ${
                    msg.role === "agent"
                      ? "bg-muted text-foreground"
                      : "bg-primary text-primary-foreground"
                  }`}>
                    <p className="font-medium text-xs mb-1 opacity-70 capitalize">{msg.role}</p>
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    <p className="text-xs opacity-50 mt-1">
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
