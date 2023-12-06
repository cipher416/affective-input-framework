
import './App.css';
import VideoRecorder from './components/ChatWindow';
import Navbar from './components/Navbar';

function App() {
  return (
    <div className="flex flex-col items-center w-full h-screen justify-center">
      <Navbar/>
      <VideoRecorder/>
    </div>
  );
}

export default App;