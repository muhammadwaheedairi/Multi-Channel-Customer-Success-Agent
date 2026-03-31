import { Zap } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t py-12 bg-muted/20">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-12 mb-12">
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-6">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground">
                <Zap size={16} fill="currentColor" />
              </div>
              <span className="text-lg font-bold tracking-tight">SupportIQ</span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Autonomous AI agents that handle customer support 24/7 — across
              every channel your customers use.
            </p>
          </div>

          <div>
            <h4 className="font-bold mb-6 text-sm uppercase tracking-widest">Product</h4>
            <ul className="space-y-4 text-sm text-muted-foreground">
              <li><a href="#features" className="hover:text-primary transition-colors">Features</a></li>
              <li><a href="#solutions" className="hover:text-primary transition-colors">How It Works</a></li>
              <li><a href="#stats" className="hover:text-primary transition-colors">Results</a></li>
              <li><a href="/dashboard" className="hover:text-primary transition-colors">Dashboard</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold mb-6 text-sm uppercase tracking-widest">Channels</h4>
            <ul className="space-y-4 text-sm text-muted-foreground">
              <li><a href="/support" className="hover:text-primary transition-colors">Web Support Form</a></li>
              <li><a href="#" className="hover:text-primary transition-colors">Email Support</a></li>
              <li><a href="#" className="hover:text-primary transition-colors">WhatsApp Support</a></li>
              <li><a href="/dashboard" className="hover:text-primary transition-colors">Live Dashboard</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold mb-6 text-sm uppercase tracking-widest">Company</h4>
            <ul className="space-y-4 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-primary transition-colors">About</a></li>
              <li><a href="#" className="hover:text-primary transition-colors">Contact</a></li>
              <li><a href="#" className="hover:text-primary transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-primary transition-colors">Terms of Service</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
          <p>© 2026 SupportIQ. All rights reserved.</p>
          <div className="flex gap-6">
            <a href="#" className="hover:text-primary transition-colors">Twitter</a>
            <a href="#" className="hover:text-primary transition-colors">LinkedIn</a>
            <a href="#" className="hover:text-primary transition-colors">GitHub</a>
          </div>
        </div>
      </div>
    </footer>
  );
}