import { useState } from 'react'
import './App.css'
import LiveKitModal from './components/LiveKitModal';

function App() {
  const [showSupport, setShowSupport] = useState(false);

  const handleSupportClick = () => {
    setShowSupport(true)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">AI Receptionist</div>
      </header>

      <main>
        <section className="hero">
          <h1>An AI voice receptionist for any business</h1>
          <p>Greets callers, answers questions, takes messages, captures appointments, and requests callbacks.</p>
          <div className="search-bar">
            <input type="text" placeholder="Try: appointment, callback, timings, message, pricing"></input>
            <button>Preview</button>
          </div>
        </section>

        <button className="support-button" onClick={handleSupportClick}>
          Talk to AI Receptionist
        </button>
      </main>

      {showSupport && <LiveKitModal setShowSupport={setShowSupport}/>}
    </div>
  )
}

export default App
