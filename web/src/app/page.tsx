import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { SteveAvatar } from "@/components/ui/SteveAvatar";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-craft-dark bg-pixel-grid">
      {/* Navigation */}
      <nav className="section-container py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <span className="text-2xl">🏗️</span>
            <span className="font-display text-lg text-craft-gold">
              Craft Architect
            </span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/login" className="nav-link">
              Log In
            </Link>
            <Link href="/signup">
              <Button variant="gold">Sign Up Free</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="section-container py-16 md:py-24">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left side - Text */}
          <div className="space-y-8">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight">
              <span className="text-craft-cream">Tell Steve what to build.</span>
              <br />
              <span className="text-gradient-gold">Watch it appear!</span>
            </h1>
            <p className="text-xl text-craft-stone-light leading-relaxed">
              Just describe your dream Minecraft build in your own words.
              Steve the Builder uses AI magic to construct it in your world instantly!
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/signup">
                <Button variant="gold" size="xl">
                  🎮 Start Building Free
                </Button>
              </Link>
              <Link href="#how-it-works">
                <Button variant="secondary" size="xl">
                  See How It Works
                </Button>
              </Link>
            </div>
            <p className="text-craft-stone-light text-sm">
              ✨ 5 free builds every month • No credit card needed
            </p>
          </div>

          {/* Right side - Steve + Demo */}
          <div className="relative">
            <div className="card-pixel p-8 relative z-10">
              {/* Chat preview */}
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <SteveAvatar size="md" mood="happy" />
                  <div className="chat-bubble-steve">
                    Hey Architect! What shall we build today?
                  </div>
                </div>
                <div className="flex items-start gap-3 flex-row-reverse">
                  <div className="w-10 h-10 rounded-full bg-craft-water flex items-center justify-center text-white font-bold">
                    A
                  </div>
                  <div className="chat-bubble-user">
                    Build me a medieval castle with towers and a moat!
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <SteveAvatar size="md" mood="building" isAnimated />
                  <div className="chat-bubble-steve">
                    Ooh, I love castles! 🏰 Building now...
                    <div className="mt-2 progress-bar">
                      <div className="progress-bar-fill" style={{ width: "75%" }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Decorative elements */}
            <div className="absolute -top-4 -right-4 w-24 h-24 bg-craft-grass/20 rounded-full blur-2xl" />
            <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-craft-water/20 rounded-full blur-2xl" />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 bg-craft-dark-lighter">
        <div className="section-container">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            How It Works
          </h2>
          <p className="text-craft-stone-light text-center text-lg mb-16 max-w-2xl mx-auto">
            Three simple steps to amazing builds. No commands to memorize!
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="card-pixel text-center space-y-4">
              <div className="w-20 h-20 mx-auto bg-craft-grass rounded-full flex items-center justify-center text-4xl">
                💬
              </div>
              <h3 className="text-xl font-bold text-craft-grass-light">
                1. Describe Your Build
              </h3>
              <p className="text-craft-stone-light">
                Tell Steve what you want in plain English.
                &quot;Build me a treehouse&quot; or &quot;Make a pirate ship&quot; - anything you can imagine!
              </p>
            </div>

            {/* Step 2 */}
            <div className="card-pixel text-center space-y-4">
              <div className="w-20 h-20 mx-auto bg-craft-gold rounded-full flex items-center justify-center text-4xl">
                🤖
              </div>
              <h3 className="text-xl font-bold text-craft-gold">
                2. Steve Gets to Work
              </h3>
              <p className="text-craft-stone-light">
                Our AI figures out the best design and materials.
                Steve places every block perfectly in seconds!
              </p>
            </div>

            {/* Step 3 */}
            <div className="card-pixel text-center space-y-4">
              <div className="w-20 h-20 mx-auto bg-craft-diamond rounded-full flex items-center justify-center text-4xl">
                🎉
              </div>
              <h3 className="text-xl font-bold text-craft-diamond">
                3. Enjoy Your Creation
              </h3>
              <p className="text-craft-stone-light">
                Your build appears in your Minecraft world instantly.
                Show off to your friends or keep building more!
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20">
        <div className="section-container">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            Simple Pricing for Young Architects
          </h2>
          <p className="text-craft-stone-light text-center text-lg mb-16">
            Start free, upgrade when you want more builds!
          </p>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Free Tier */}
            <div className="card-pixel space-y-6">
              <div className="text-center">
                <span className="badge-free mb-4 inline-block">Free</span>
                <h3 className="text-2xl font-bold text-craft-cream">Starter</h3>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-craft-cream">$0</span>
                  <span className="text-craft-stone-light">/month</span>
                </div>
              </div>
              <ul className="space-y-3 text-craft-stone-light">
                <li className="flex items-center gap-2">
                  <span className="text-craft-grass">✓</span>
                  5 builds per month
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-craft-grass">✓</span>
                  1 server connection
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-craft-grass">✓</span>
                  Basic structures
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-craft-grass">✓</span>
                  Build history
                </li>
              </ul>
              <Link href="/signup" className="block">
                <Button variant="secondary" className="w-full">
                  Get Started Free
                </Button>
              </Link>
            </div>

            {/* Builder Tier */}
            <div className="card-pixel space-y-6 border-craft-gold border-2 relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="bg-craft-gold text-craft-dark px-4 py-1 rounded-full text-sm font-bold">
                  POPULAR
                </span>
              </div>
              <div className="text-center">
                <span className="badge-builder mb-4 inline-block">Builder</span>
                <h3 className="text-2xl font-bold text-craft-cream">Builder</h3>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-craft-gold">$5</span>
                  <span className="text-craft-stone-light">/month</span>
                </div>
              </div>
              <ul className="space-y-3 text-craft-stone-light">
                <li className="flex items-center gap-2">
                  <span className="text-craft-gold">✓</span>
                  <strong className="text-craft-cream">50 builds</strong> per month
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-craft-gold">✓</span>
                  3 server connections
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-craft-gold">✓</span>
                  Complex structures
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-craft-gold">✓</span>
                  Priority building
                </li>
              </ul>
              <Link href="/signup?plan=builder" className="block">
                <Button variant="gold" className="w-full">
                  Choose Builder
                </Button>
              </Link>
            </div>

            {/* Architect Tier */}
            <div className="card-pixel space-y-6">
              <div className="text-center">
                <span className="badge-architect mb-4 inline-block">Architect</span>
                <h3 className="text-2xl font-bold text-craft-cream">Architect</h3>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-craft-diamond">$10</span>
                  <span className="text-craft-stone-light">/month</span>
                </div>
              </div>
              <ul className="space-y-3 text-craft-stone-light">
                <li className="flex items-center gap-2">
                  <span className="text-craft-diamond">✓</span>
                  <strong className="text-craft-cream">Unlimited</strong> builds
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-craft-diamond">✓</span>
                  Unlimited servers
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-craft-diamond">✓</span>
                  Mega structures
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-craft-diamond">✓</span>
                  Early access features
                </li>
              </ul>
              <Link href="/signup?plan=architect" className="block">
                <Button variant="primary" className="w-full">
                  Choose Architect
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-craft-grass/20 to-craft-water/20">
        <div className="section-container text-center space-y-8">
          <SteveAvatar size="xl" mood="waving" isAnimated className="mx-auto" />
          <h2 className="text-3xl md:text-4xl font-bold">
            Ready to Start Building?
          </h2>
          <p className="text-xl text-craft-stone-light max-w-2xl mx-auto">
            Join thousands of young architects who are creating amazing
            Minecraft builds with just their imagination!
          </p>
          <Link href="/signup">
            <Button variant="gold" size="xl">
              🚀 Start Building for Free
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-craft-stone-dark">
        <div className="section-container">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🏗️</span>
              <span className="font-display text-sm text-craft-gold">
                Craft Architect
              </span>
            </div>
            <p className="text-craft-stone-light text-sm">
              Made with ❤️ for young builders everywhere
            </p>
            <div className="flex gap-6 text-sm text-craft-stone-light">
              <Link href="/privacy" className="hover:text-craft-cream">Privacy</Link>
              <Link href="/terms" className="hover:text-craft-cream">Terms</Link>
              <Link href="/help" className="hover:text-craft-cream">Help</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
