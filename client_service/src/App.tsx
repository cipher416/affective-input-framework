
import './App.css';
import VideoRecorder from './components/VideoRecorder';

function App() {
  return (
    <div className="flex flex-col items-center w-full min-h-screen justify-center bg-gray-900">
      <h1 className='text-white py-3'>
        Affective Input Framework Test
      </h1>
      <VideoRecorder/>
    </div>
  );
}

export default App;