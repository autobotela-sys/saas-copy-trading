'use client';

import { Layout } from '@/components/layout/Layout';
import { TopNavbar } from '@/components/layout/TopNavbar';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { useRequireAuth } from '@/hooks/useAuth';
import { useState } from 'react';

export default function SupportPage() {
  const { user, loading } = useRequireAuth();
  const [expandedFaq, setExpandedFaq] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const faqs = [
    {
      id: '1',
      question: 'How do I link my broker account?',
      answer: 'Go to Portfolio > Broker Account and click "Add Broker Account". Select your broker (Zerodha or Dhan) and enter your API credentials. Follow the OAuth flow to authorize access.',
    },
    {
      id: '2',
      question: 'What is lot size multiplier?',
      answer: 'Lot size multiplier determines how much you trade relative to the admin broadcast. For example, if admin broadcasts 1 lot (30 qty) and you set 2X, you will trade 60 qty.',
    },
    {
      id: '3',
      question: 'How do I refresh my broker token?',
      answer: 'Go to Portfolio > Broker Account and click "Generate Token". This will open your broker\'s authorization page where you can approve access.',
    },
    {
      id: '4',
      question: 'Why was my order not executed?',
      answer: 'Orders may fail due to: insufficient margin, market hours, invalid strike price, or expired broker token. Check your broker token status and ensure you have sufficient margin.',
    },
    {
      id: '5',
      question: 'How do I close a position?',
      answer: 'Go to your Dashboard, find the position in the Open Positions table, and click the "Close" button. You can do a full close or partial close.',
    },
    {
      id: '6',
      question: 'Is my API key safe?',
      answer: 'Yes. We store your broker credentials securely using encryption. Your API key is only used to communicate with your broker and is never shared.',
    },
  ];

  const toggleFaq = (id: string) => {
    setExpandedFaq(expandedFaq === id ? null : id);
  };

  const handleContactSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In production, this would submit to backend
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-[#49879c]">Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <TopNavbar title="Help & Support" />
      <div className="p-8 max-w-5xl mx-auto">
        {/* Quick Help */}
        <div className="bg-gradient-to-r from-primary to-blue-600 rounded-xl p-8 mb-8 text-white">
          <h2 className="text-2xl font-bold mb-2">How can we help you?</h2>
          <p className="text-white/80 mb-6">Find answers to common questions or get in touch with our support team.</p>
          <div className="flex flex-wrap gap-4">
            <a href="#faq" className="bg-white text-primary px-4 py-2 rounded-lg font-semibold hover:bg-white/90 transition-colors">
              Browse FAQs
            </a>
            <a href="#contact" className="bg-white/20 text-white px-4 py-2 rounded-lg font-semibold hover:bg-white/30 transition-colors">
              Contact Support
            </a>
          </div>
        </div>

        {/* FAQ Section */}
        <div id="faq" className="mb-12">
          <h3 className="text-2xl font-bold text-[#0d181c] dark:text-white mb-6">Frequently Asked Questions</h3>
          <div className="space-y-3">
            {faqs.map((faq) => (
              <div
                key={faq.id}
                className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 overflow-hidden"
              >
                <button
                  className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                  onClick={() => toggleFaq(faq.id)}
                >
                  <span className="font-semibold text-[#0d181c] dark:text-white">{faq.question}</span>
                  <span
                    className={`material-symbols-outlined transition-transform ${
                      expandedFaq === faq.id ? 'rotate-180' : ''
                    }`}
                  >
                    expand_more
                  </span>
                </button>
                {expandedFaq === faq.id && (
                  <div className="px-6 pb-4 pt-2 text-[#49879c] border-t border-[#cee2e8] dark:border-gray-800">
                    {faq.answer}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Contact Form */}
        <div id="contact" className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-8">
          <h3 className="text-2xl font-bold text-[#0d181c] dark:text-white mb-2">Contact Support</h3>
          <p className="text-[#49879c] mb-6">Can't find what you're looking for? Send us a message.</p>

          {submitted ? (
            <div className="bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-400 px-4 py-3 rounded-lg text-sm">
              <p className="font-semibold">Message sent successfully!</p>
              <p className="text-sm mt-1">Our support team will get back to you within 24 hours.</p>
            </div>
          ) : (
            <form onSubmit={handleContactSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Name"
                  placeholder="Your name"
                  defaultValue={user?.email?.split('@')[0]}
                  required
                />
                <Input
                  label="Email"
                  type="email"
                  placeholder="your@email.com"
                  defaultValue={user?.email}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Subject</label>
                <select className="w-full px-3 py-2 border border-[#cee2e8] dark:border-gray-700 rounded-lg bg-white dark:bg-background-dark text-[#0d181c] dark:text-white focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="">Select a topic</option>
                  <option value="broker">Broker Connection Issue</option>
                  <option value="order">Order Execution Problem</option>
                  <option value="account">Account & Billing</option>
                  <option value="technical">Technical Issue</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Message</label>
                <textarea
                  required
                  rows={5}
                  placeholder="Describe your issue in detail..."
                  className="w-full px-3 py-2 border border-[#cee2e8] dark:border-gray-700 rounded-lg bg-white dark:bg-background-dark text-[#0d181c] dark:text-white focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                />
              </div>

              <Button type="submit" variant="primary" size="lg">
                Send Message
              </Button>
            </form>
          )}
        </div>

        {/* Contact Info */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6 text-center">
            <span className="material-symbols-outlined text-4xl text-primary mb-2">email</span>
            <h4 className="font-semibold mb-1">Email</h4>
            <p className="text-sm text-[#49879c]">support@zapcopytrading.com</p>
          </div>
          <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6 text-center">
            <span className="material-symbols-outlined text-4xl text-primary mb-2">phone</span>
            <h4 className="font-semibold mb-1">Phone</h4>
            <p className="text-sm text-[#49879c]">+91 XXXXX XXXXX</p>
          </div>
          <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6 text-center">
            <span className="material-symbols-outlined text-4xl text-primary mb-2">schedule</span>
            <h4 className="font-semibold mb-1">Support Hours</h4>
            <p className="text-sm text-[#49879c]">Mon-Fri, 9AM-6PM IST</p>
          </div>
        </div>
      </div>
    </Layout>
  );
}
