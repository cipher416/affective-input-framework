import { useState, useEffect, useRef, FormEvent } from "react";
import RecordRTC, { getSeekableBlob} from "recordrtc";
import axios from "axios";
import ChatBubble from "./ChatBubble";


const VideoRecorder = () => {
    const [stream, setStream] = useState<MediaStream | null>(null);
    const refVideo = useRef<any>(null);
    const recorderRef = useRef<RecordRTC | null>(null);
    const [recording, setRecording] = useState<boolean>(false);
    const [chats, setChats] = useState<Chat[]>([]);
    const [input, setInput] = useState<string>("");
    const handleRecording = async () => {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      setStream(mediaStream);
      recorderRef.current = new RecordRTC(mediaStream, { type: 'video', mimeType:'video/webm', numberOfAudioChannels: 1});
      recorderRef.current.startRecording();
      setRecording(true);
    };
  
    const handleStop = async () => {
      if (recorderRef.current) {
        recorderRef.current.stopRecording(async () => {
            if (recorderRef.current) 
            {
                const blob = recorderRef.current.getBlob();
                getSeekableBlob(blob, async (output) => {
                  const file = new File([output], 'video.webm');
                  const formData = new FormData();
                  formData.append('file', file);
                  const result = await axios.post(import.meta.env.VITE_BACKEND_URL!, formData, {headers: { "Content-Type": "multipart/form-data" }});
                  const resultBody = result.data;
                  const chat: Chat = {
                    message: resultBody.message,
                    emotion: resultBody.emotion,
                    sender: "bot"
                  }
                  const userChat: Chat = {
                    message: resultBody.speech_transcript,
                    emotion: resultBody.emotion,
                    sender: "user"
                  }
                  setChats(chats.concat([userChat, chat]));
                  recorderRef.current!.reset();
                  setRecording(false);
                })
            }
        }); 
      }
    };

    async function onFormSubmit(e: FormEvent) {
      e.preventDefault()
      setRecording(true);
      setInput('');
      const result = await axios.post(`${import.meta.env.VITE_BACKEND_URL!}/text`, {
        "message" : input
      }, {headers: { "Content-Type": "application/json" }});
      const resultBody = result.data;
      const chat: Chat = {
        message: resultBody.message,
        emotion: resultBody.emotion,
        sender: "bot"
      }
      const userChat: Chat = {
        message: resultBody.speech_transcript,
        emotion: resultBody.emotion,
        sender: "user"
      }
      console.log(resultBody)
      setChats(chats.concat([userChat, chat]));
      console.log(chats);
      setRecording(false);
    }

  
    useEffect(() => {
      if (!refVideo.current) {
        return;
      }
      
    refVideo.current.srcObject = stream;
    }, [stream, refVideo, chats]);
    

    return (
        <div className="flex flex-col w-full">
                <div className="flex flex-col justify-center items-center rounded-s-sm">
                  <div className="p-10 justify-end min-w-full overflow-y-scroll h-[75vh] max-h-[70vh]">
                    {chats.map(chat => {
                        return <ChatBubble key={''} chat={chat}/>
                      })}
                    {recording ? <ChatBubble isLoading/> : <></>}
                  </div>
                  <div className="divider"/>
                  <div className="flex flex-row w-full m-0 px-2">
                    <form onSubmit={onFormSubmit} className="w-full me-5">
                      <input type="text" placeholder="Type here"  value={input} onChange={(e)=> setInput(e.target.value)} className='input input-bordered w-full self-center mx-2'  disabled={recording}/>  
                    </form>
                    <button className={`btn btn-circle bg-red-700 hover:bg-red-900 ${recording ? "btn-outline": ""}`} onClick={recording ? handleStop : handleRecording}>
                      <img src="mic-icon.svg" className="h-1/2 invert"/>
                    </button>
                  </div>
                </div>
        </div>
    );
};
export default VideoRecorder;