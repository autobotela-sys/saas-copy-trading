'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { authApi } from '@/lib/api';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';

interface ForgotPasswordForm {
  email: string;
}

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordForm>();

  const onSubmit = async (data: ForgotPasswordForm) => {
    setError('');
    setLoading(true);
    try {
      await authApi.forgotPassword(data.email);
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Failed to send reset email. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-background-light dark:bg-background-dark font-display min-h-screen flex items-center justify-center p-0 m-0">
      <div className="flex h-screen w-full overflow-hidden">
        {/* Left Side: Branding/Hero Pane */}
        <div className="hidden lg:flex flex-col justify-center items-center w-1/2 bg-background-dark text-white p-12 relative overflow-hidden">
          <div className="absolute inset-0 opacity-10 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, #0db9f2 1px, transparent 0)', backgroundSize: '40px 40px' }}></div>
          <div className="relative z-10 max-w-lg">
            <div className="flex items-center gap-3 mb-8">
              <div className="size-12 bg-primary rounded-xl flex items-center justify-center">
                <svg className="w-8 h-8 text-background-dark" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                  <path clipRule="evenodd" d="M39.475 21.6262C40.358 21.4363 40.6863 21.5589 40.7581 21.5934C40.7876 21.655 40.8547 21.857 40.8082 22.3336C40.7408 23.0255 40.4502 24.0046 39.8572 25.2301C38.6799 27.6631 36.5085 30.6631 33.5858 33.5858C30.6631 36.5085 27.6632 38.6799 25.2301 39.8572C24.0046 40.4502 23.0255 40.7407 22.3336 40.8082C21.8571 40.8547 21.6551 40.7875 21.5934 40.7581C21.5589 40.6863 21.4363 40.358 21.6262 39.475C21.8562 38.4054 22.4689 36.9657 23.5038 35.2817C24.7575 33.2417 26.5497 30.9744 28.7621 28.762C30.9744 26.5497 33.2417 24.7574 35.2817 23.5037C36.9657 22.4689 38.4054 21.8562 39.475 21.6262ZM4.41189 29.2403L18.7597 43.5881C19.8813 44.7097 21.4027 44.9179 22.7217 44.7893C24.0585 44.659 25.5148 44.1631 26.9723 43.4579C29.9052 42.0387 33.2618 39.5667 36.4142 36.4142C39.5667 33.2618 42.0387 29.9052 43.4579 26.9723C44.1631 25.5148 44.659 24.0585 44.7893 22.7217C44.9179 21.4027 44.7097 19.8813 43.5881 18.7597L29.2403 4.41187C27.8527 3.02428 25.8765 3.02573 24.2861 3.36776C22.6081 3.72863 20.7334 4.58419 18.8396 5.74801C16.4978 7.18716 13.9881 9.18353 11.5858 11.5858C9.18354 13.988 7.18717 16.4978 5.74802 18.8396C4.58421 20.7334 3.72865 22.6081 3.36778 24.2861C3.02574 25.8765 3.02429 27.8527 4.41189 29.2403Z" fill="currentColor" fillRule="evenodd"></path>
                </svg>
              </div>
              <h1 className="text-3xl font-black tracking-tight">Zap Copy Trading</h1>
            </div>
            <h2 className="text-4xl font-bold leading-tight mb-6">Reset Your Password</h2>
            <p className="text-lg text-slate-400 mb-8 leading-relaxed">
              Enter your email address and we'll send you a link to reset your password.
            </p>
          </div>
        </div>

        {/* Right Side: Forgot Password Form */}
        <div className="w-full lg:w-1/2 flex flex-col justify-center items-center bg-background-light dark:bg-background-dark px-6 py-12">
          <div className="w-full max-w-[440px] flex flex-col gap-8">
            {/* Mobile Logo Header */}
            <div className="lg:hidden flex items-center gap-3 mb-2">
              <div className="size-8 bg-primary rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-background-dark" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                  <path clipRule="evenodd" d="M39.475 21.6262C40.358 21.4363 40.6863 21.5589 40.7581 21.5934C40.7876 21.655 40.8547 21.857 40.8082 22.3336C40.7408 23.0255 40.4502 24.0046 39.8572 25.2301C38.6799 27.6631 36.5085 30.6631 33.5858 33.5858C30.6631 36.5085 27.6632 38.6799 25.2301 39.8572C24.0046 40.4502 23.0255 40.7407 22.3336 40.8082C21.8571 40.8547 21.6551 40.7875 21.5934 40.7581C21.5589 40.6863 21.4363 40.358 21.6262 39.475C21.8562 38.4054 22.4689 36.9657 23.5038 35.2817C24.7575 33.2417 26.5497 30.9744 28.7621 28.762C30.9744 26.5497 33.2417 24.7574 35.2817 23.5037C36.9657 22.4689 38.4054 21.8562 39.475 21.6262ZM4.41189 29.2403L18.7597 43.5881C19.8813 44.7097 21.4027 44.9179 22.7217 44.7893C24.0585 44.659 25.5148 44.1631 26.9723 43.4579C29.9052 42.0387 33.2618 39.5667 36.4142 36.4142C39.5667 33.2618 42.0387 29.9052 43.4579 26.9723C44.1631 25.5148 44.659 24.0585 44.7893 22.7217C44.9179 21.4027 44.7097 19.8813 43.5881 18.7597L29.2403 4.41187C27.8527 3.02428 25.8765 3.02573 24.2861 3.36776C22.6081 3.72863 20.7334 4.58419 18.8396 5.74801C16.4978 7.18716 13.9881 9.18353 11.5858 11.5858C9.18354 13.988 7.18717 16.4978 5.74802 18.8396C4.58421 20.7334 3.72865 22.6081 3.36778 24.2861C3.02574 25.8765 3.02429 27.8527 4.41189 29.2403Z" fill="currentColor" fillRule="evenodd"></path>
                </svg>
              </div>
              <span className="text-xl font-bold dark:text-white">Zap Copy Trading</span>
            </div>

            <div className="flex flex-col gap-2">
              <h2 className="text-[#0d181c] dark:text-white text-3xl font-bold leading-tight tracking-tight">
                Forgot Password?
              </h2>
              <p className="text-slate-500 dark:text-slate-400">No worries, we'll send you reset instructions.</p>
            </div>

            {error && (
              <div className="bg-rose-50 dark:bg-rose-900/30 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-400 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {success ? (
              <div className="bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-400 px-4 py-3 rounded-lg text-sm">
                <p className="font-semibold mb-2">Check your email</p>
                <p className="text-sm">We've sent a password reset link to your email address. Please check your inbox and follow the instructions.</p>
                <div className="mt-4">
                  <Link href="/login" className="text-primary font-bold hover:underline text-sm">
                    Back to Login
                  </Link>
                </div>
              </div>
            ) : (
              <>
                <form className="flex flex-col gap-6" onSubmit={handleSubmit(onSubmit)}>
                  <Input
                    label="Email Address"
                    type="email"
                    placeholder="name@company.com"
                    {...register('email', {
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address',
                      },
                    })}
                    error={errors.email?.message}
                  />

                  <Button type="submit" variant="primary" size="lg" className="w-full" disabled={loading}>
                    {loading ? 'Sending...' : 'Send Reset Link'}
                  </Button>
                </form>

                <p className="text-center text-sm text-[#49879c]">
                  Remember your password?{' '}
                  <Link href="/login" className="text-primary font-bold hover:underline">
                    Back to Login
                  </Link>
                </p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
