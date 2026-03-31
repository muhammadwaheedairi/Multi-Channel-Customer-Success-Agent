"use client"

import { useState } from "react"
import { submitSupportForm } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"

const CATEGORIES = [
  { value: "general", label: "General Question" },
  { value: "technical", label: "Technical Support" },
  { value: "billing", label: "Billing Inquiry" },
  { value: "bug_report", label: "Bug Report" },
  { value: "feedback", label: "Feedback" },
]

const PRIORITIES = [
  { value: "low", label: "Low — Not urgent" },
  { value: "medium", label: "Medium — Need help soon" },
  { value: "high", label: "High — Urgent issue" },
]

export default function SupportPage() {
  const [form, setForm] = useState({
    name: "", email: "", subject: "",
    category: "general", priority: "medium", message: "",
  })
  const [status, setStatus] = useState<"idle"|"submitting"|"success"|"error">("idle")
  const [ticketId, setTicketId] = useState("")
  const [error, setError] = useState("")

  const handleChange = (field: string, value: string) =>
    setForm(prev => ({ ...prev, [field]: value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    if (form.name.trim().length < 2) return setError("Name must be at least 2 characters")
    if (form.message.trim().length < 10) return setError("Message must be at least 10 characters")
    setStatus("submitting")
    try {
      const data = await submitSupportForm(form)
      setTicketId(data.ticket_id)
      setStatus("success")
    } catch (err: any) {
      setError(err.message)
      setStatus("error")
    }
  }

  if (status === "success") {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="w-full max-w-md text-center">
          <CardHeader>
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <CardTitle>Request Submitted!</CardTitle>
            <CardDescription>Our AI agent will respond shortly.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-muted rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-1">Your Ticket ID</p>
              <p className="font-mono font-bold text-sm break-all">{ticketId}</p>
            </div>
            <a href={`/support/ticket/${ticketId}`}>
              <Button className="w-full">Track Your Ticket →</Button>
            </a>
            <Button variant="outline" className="w-full"
              onClick={() => { setStatus("idle"); setTicketId(""); setForm({ name:"", email:"", subject:"", category:"general", priority:"medium", message:"" }) }}>
              Submit Another Request
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="secondary">24/7 AI Support</Badge>
          </div>
          <CardTitle className="text-2xl">Contact Support</CardTitle>
          <CardDescription>
            Fill out the form below. Our AI agent responds within 5 minutes.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name *</Label>
                <Input id="name" placeholder="Sara Khan"
                  value={form.name} onChange={e => handleChange("name", e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email Address *</Label>
                <Input id="email" type="email" placeholder="sara@example.com"
                  value={form.email} onChange={e => handleChange("email", e.target.value)} required />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="subject">Subject *</Label>
              <Input id="subject" placeholder="Brief description of your issue"
                value={form.subject} onChange={e => handleChange("subject", e.target.value)} required />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Category *</Label>
                <Select value={form.category} onValueChange={v => handleChange("category", v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {CATEGORIES.map(c => <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Priority</Label>
                <Select value={form.priority} onValueChange={v => handleChange("priority", v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {PRIORITIES.map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="message">How can we help? *</Label>
              <Textarea id="message" rows={5}
                placeholder="Please describe your issue in detail..."
                value={form.message} onChange={e => handleChange("message", e.target.value)} required />
              <p className="text-xs text-muted-foreground text-right">{form.message.length}/1000</p>
            </div>
            <Button type="submit" className="w-full" disabled={status === "submitting"}>
              {status === "submitting" ? "Submitting..." : "Submit Support Request"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
