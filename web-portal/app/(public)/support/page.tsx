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
import { motion, AnimatePresence } from "framer-motion"
import {
  CheckCircle2,
  Sparkles,
  Send,
  ArrowRight,
  AlertCircle,
  Zap,
  Clock,
  MessageSquare
} from "lucide-react"
import Link from "next/link"
import Header from "@/components/Header"
import Footer from "@/components/Footer"

const CATEGORIES = [
  { value: "general", label: "General Question", icon: "💬", color: "bg-blue-500/10" },
  { value: "technical", label: "Technical Support", icon: "⚙️", color: "bg-purple-500/10" },
  { value: "billing", label: "Billing Inquiry", icon: "💳", color: "bg-green-500/10" },
  { value: "bug_report", label: "Bug Report", icon: "🐛", color: "bg-red-500/10" },
  { value: "feedback", label: "Feedback", icon: "⭐", color: "bg-yellow-500/10" },
]

const PRIORITIES = [
  { value: "low", label: "Low — Not urgent", color: "text-green-600" },
  { value: "medium", label: "Medium — Need help soon", color: "text-yellow-600" },
  { value: "high", label: "High — Urgent issue", color: "text-red-600" },
]

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.4 }
}

const scaleIn = {
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
  transition: { duration: 0.5, type: "spring" }
}

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
      <div className="min-h-screen bg-background text-foreground">
        <Header />

        <div className="relative min-h-screen flex items-center justify-center p-4 sm:p-6 pt-24 sm:pt-28 pb-12 overflow-hidden">
          {/* Animated Background */}
          <div className="absolute inset-0 -z-10 opacity-30">
            <div className="absolute top-0 left-1/4 w-64 h-64 sm:w-96 sm:h-96 bg-green-500/20 rounded-full blur-[120px] animate-pulse" />
            <div className="absolute bottom-0 right-1/4 w-64 h-64 sm:w-96 sm:h-96 bg-blue-500/20 rounded-full blur-[120px]" />
            <div className="absolute top-1/2 left-1/2 w-64 h-64 sm:w-96 sm:h-96 bg-purple-500/10 rounded-full blur-[120px]" />
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, type: "spring" }}
            className="w-full max-w-2xl"
          >
            <Card className="border-none shadow-2xl bg-background/80 backdrop-blur-xl">
              <CardHeader className="text-center pb-6 sm:pb-8">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                  className="w-20 h-20 sm:w-24 sm:h-24 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center mx-auto mb-4 sm:mb-6 shadow-lg shadow-green-500/50"
                >
                  <CheckCircle2 className="w-10 h-10 sm:w-12 sm:h-12 text-white" strokeWidth={3} />
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <CardTitle className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-2 sm:mb-3">
                    Request Submitted Successfully!
                  </CardTitle>
                  <CardDescription className="text-base sm:text-lg">
                    Our AI agent is processing your request right now
                  </CardDescription>
                </motion.div>
              </CardHeader>

              <CardContent className="space-y-4 sm:space-y-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="bg-gradient-to-br from-primary/10 to-primary/5 rounded-2xl p-4 sm:p-6 border border-primary/20"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 bg-primary/20 rounded-xl flex items-center justify-center">
                      <Sparkles className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-xs sm:text-sm font-medium text-muted-foreground">Your Ticket ID</p>
                      <p className="font-mono font-bold text-lg sm:text-xl">{ticketId.slice(0, 8)}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2 sm:gap-3 mt-4 sm:mt-6">
                    <div className="text-center p-2 sm:p-3 bg-background/50 rounded-xl">
                      <Clock className="w-4 h-4 sm:w-5 sm:h-5 mx-auto mb-1 text-primary" />
                      <p className="text-[10px] sm:text-xs text-muted-foreground">Response in</p>
                      <p className="text-xs sm:text-sm font-bold">~3 seconds</p>
                    </div>
                    <div className="text-center p-2 sm:p-3 bg-background/50 rounded-xl">
                      <Zap className="w-4 h-4 sm:w-5 sm:h-5 mx-auto mb-1 text-primary" />
                      <p className="text-[10px] sm:text-xs text-muted-foreground">AI Powered</p>
                      <p className="text-xs sm:text-sm font-bold">GPT-4o</p>
                    </div>
                    <div className="text-center p-2 sm:p-3 bg-background/50 rounded-xl">
                      <MessageSquare className="w-4 h-4 sm:w-5 sm:h-5 mx-auto mb-1 text-primary" />
                      <p className="text-[10px] sm:text-xs text-muted-foreground">Status</p>
                      <p className="text-xs sm:text-sm font-bold">Processing</p>
                    </div>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                  className="space-y-3"
                >
                  <Link href={`/support/ticket/${ticketId}`}>
                    <Button size="lg" className="w-full h-12 sm:h-14 text-base sm:text-lg font-bold group shadow-xl shadow-primary/20">
                      Track Your Ticket
                      <ArrowRight className="ml-2 transition-transform group-hover:translate-x-1" />
                    </Button>
                  </Link>

                  <Button
                    size="lg"
                    variant="outline"
                    className="w-full h-12 sm:h-14 text-base sm:text-lg font-bold"
                    onClick={() => {
                      setStatus("idle");
                      setTicketId("");
                      setForm({ name:"", email:"", subject:"", category:"general", priority:"medium", message:"" })
                    }}
                  >
                    Submit Another Request
                  </Button>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6 }}
                  className="flex items-center justify-center gap-2 text-xs sm:text-sm text-muted-foreground pt-4"
                >
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                  </span>
                  AI Agent is analyzing your request
                </motion.div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        <Footer />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      <div className="relative min-h-screen flex items-center justify-center p-4 sm:p-6 pt-24 sm:pt-28 pb-12 overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 -z-10 opacity-30">
          <div className="absolute top-0 left-1/4 w-64 h-64 sm:w-96 sm:h-96 bg-primary/20 rounded-full blur-[120px] animate-pulse" />
          <div className="absolute bottom-0 right-1/4 w-64 h-64 sm:w-96 sm:h-96 bg-purple-500/20 rounded-full blur-[120px]" />
          <div className="absolute top-1/2 left-1/2 w-64 h-64 sm:w-96 sm:h-96 bg-blue-500/10 rounded-full blur-[120px]" />
        </div>

        <motion.div
          initial="initial"
          animate="animate"
          variants={scaleIn}
          className="w-full max-w-3xl"
        >
          <Card className="border-none shadow-2xl bg-background/80 backdrop-blur-xl">
            <CardHeader className="space-y-3 sm:space-y-4">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="flex items-center gap-3"
              >
                <div className="relative">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-primary to-primary/60 rounded-2xl flex items-center justify-center shadow-lg shadow-primary/30">
                    <Send className="w-5 h-5 sm:w-6 sm:h-6 text-primary-foreground" />
                  </div>
                  <span className="absolute -top-1 -right-1 flex h-3 w-3 sm:h-4 sm:w-4">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 sm:h-4 sm:w-4 bg-green-500 border-2 border-background"></span>
                  </span>
                </div>
                <div>
                  <Badge variant="secondary" className="mb-2 text-xs">24/7 AI Support</Badge>
                  <CardTitle className="text-2xl sm:text-3xl font-bold">Contact Support</CardTitle>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <CardDescription className="text-sm sm:text-base">
                  Fill out the form below. Our AI agent responds within <span className="font-bold text-primary">5 minutes</span>.
                </CardDescription>
              </motion.div>
            </CardHeader>

            <CardContent>
              <AnimatePresence mode="wait">
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="mb-4 sm:mb-6 p-3 sm:p-4 bg-destructive/10 border border-destructive/20 rounded-xl flex items-start gap-3"
                  >
                    <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                    <p className="text-xs sm:text-sm text-destructive font-medium">{error}</p>
                  </motion.div>
                )}
              </AnimatePresence>

              <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5"
                >
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-xs sm:text-sm font-semibold">Full Name *</Label>
                    <Input
                      id="name"
                      placeholder="Sara Khan"
                      className="h-11 sm:h-12 text-sm sm:text-base bg-background/50 border-border/50 focus:border-primary transition-all"
                      value={form.name}
                      onChange={e => handleChange("name", e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-xs sm:text-sm font-semibold">Email Address *</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="sara@example.com"
                      className="h-11 sm:h-12 text-sm sm:text-base bg-background/50 border-border/50 focus:border-primary transition-all"
                      value={form.email}
                      onChange={e => handleChange("email", e.target.value)}
                      required
                    />
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="space-y-2"
                >
                  <Label htmlFor="subject" className="text-xs sm:text-sm font-semibold">Subject *</Label>
                  <Input
                    id="subject"
                    placeholder="Brief description of your issue"
                    className="h-11 sm:h-12 text-sm sm:text-base bg-background/50 border-border/50 focus:border-primary transition-all"
                    value={form.subject}
                    onChange={e => handleChange("subject", e.target.value)}
                    required
                  />
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5"
                >
                  <div className="space-y-2">
                    <Label className="text-xs sm:text-sm font-semibold">Category *</Label>
                    <Select value={form.category} onValueChange={v => handleChange("category", v)}>
                      <SelectTrigger className="h-11 sm:h-12 text-sm sm:text-base bg-card border-input">
                        <SelectValue>
                          <span className="flex items-center gap-2">
                            <span>{CATEGORIES.find(c => c.value === form.category)?.icon}</span>
                            <span>{CATEGORIES.find(c => c.value === form.category)?.label}</span>
                          </span>
                        </SelectValue>
                      </SelectTrigger>
                      <SelectContent className="bg-popover border-border shadow-lg backdrop-blur-xl z-50">
                        {CATEGORIES.map(c => (
                          <SelectItem
                            key={c.value}
                            value={c.value}
                            className="cursor-pointer hover:bg-accent focus:bg-accent"
                          >
                            <span className="flex items-center gap-2 text-sm sm:text-base">
                              <span>{c.icon}</span>
                              <span>{c.label}</span>
                            </span>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs sm:text-sm font-semibold">Priority</Label>
                    <Select value={form.priority} onValueChange={v => handleChange("priority", v)}>
                      <SelectTrigger className="h-11 sm:h-12 text-sm sm:text-base bg-card border-input">
                        <SelectValue>
                          <span className={PRIORITIES.find(p => p.value === form.priority)?.color}>
                            {PRIORITIES.find(p => p.value === form.priority)?.label}
                          </span>
                        </SelectValue>
                      </SelectTrigger>
                      <SelectContent className="bg-popover border-border shadow-lg backdrop-blur-xl z-50">
                        {PRIORITIES.map(p => (
                          <SelectItem
                            key={p.value}
                            value={p.value}
                            className="cursor-pointer hover:bg-accent focus:bg-accent"
                          >
                            <span className={`${p.color} text-sm sm:text-base font-medium`}>{p.label}</span>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 }}
                  className="space-y-2"
                >
                  <Label htmlFor="message" className="text-xs sm:text-sm font-semibold">How can we help? *</Label>
                  <Textarea
                    id="message"
                    rows={6}
                    placeholder="Please describe your issue in detail..."
                    className="text-sm sm:text-base bg-background/50 border-border/50 focus:border-primary transition-all resize-none"
                    value={form.message}
                    onChange={e => handleChange("message", e.target.value)}
                    required
                  />
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">
                      {form.message.length < 10 ? "Minimum 10 characters" : "Looking good!"}
                    </span>
                    <span className={`font-medium ${form.message.length > 900 ? "text-destructive" : "text-muted-foreground"}`}>
                      {form.message.length}/1000
                    </span>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 }}
                >
                  <Button
                    type="submit"
                    size="lg"
                    className="w-full h-12 sm:h-14 text-base sm:text-lg font-bold group shadow-xl shadow-primary/20"
                    disabled={status === "submitting"}
                  >
                    {status === "submitting" ? (
                      <>
                        <span className="animate-pulse">Processing...</span>
                      </>
                    ) : (
                      <>
                        Submit Support Request
                        <Send className="ml-2 transition-transform group-hover:translate-x-1" size={20} />
                      </>
                    )}
                  </Button>
                </motion.div>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <Footer />
    </div>
  )
}
