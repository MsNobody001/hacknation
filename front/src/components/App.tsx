import { Route, Routes } from 'react-router-dom';

import { VictimExplanationForm } from '@/pages';
import { Message } from '@/types';
import { ChatWidget } from './ChatWidget';

const App = () => {
  const initialHistory: Message[] = [
    {
      id: '1',
      text: '1',
      sender: 'agent',
      timestamp: new Date(Date.now() - 1000 * 60 * 60), // 1 hour ago
    },
    {
      id: '2',
      text: '2',
      sender: 'user',
      timestamp: new Date(Date.now() - 1000 * 60 * 55),
    },
    {
      id: '3',
      text: '3',
      sender: 'agent',
      timestamp: new Date(Date.now() - 1000 * 60 * 50), // 1 hour ago
    },
    {
      id: '4',
      text: '4',
      sender: 'user',
      timestamp: new Date(Date.now() - 1000 * 60 * 45),
    },
    {
      id: '5',
      text: '5',
      sender: 'agent',
      timestamp: new Date(Date.now() - 1000 * 60 * 40), // 1 hour ago
    },
    {
      id: '6',
      text: '6',
      sender: 'user',
      timestamp: new Date(Date.now() - 1000 * 60 * 35),
    },
    {
      id: '7',
      text: '7',
      sender: 'agent',
      timestamp: new Date(Date.now() - 1000 * 60 * 30), // 1 hour ago
    },
    {
      id: '8',
      text: '8',
      sender: 'user',
      timestamp: new Date(Date.now() - 1000 * 60 * 25),
    },
    {
      id: '9',
      text: '9',
      sender: 'agent',
      timestamp: new Date(Date.now() - 1000 * 60 * 20), // 1 hour ago
    },
    {
      id: '10',
      text: '10',
      sender: 'user',
      timestamp: new Date(Date.now() - 1000 * 60 * 15),
    },
        {
      id: '11',
      text: '11',
      sender: 'agent',
      timestamp: new Date(Date.now() - 1000 * 60 * 10), // 1 hour ago
    },
    {
      id: '12',
      text: '12',
      sender: 'user',
      timestamp: new Date(Date.now() - 1000 * 60 * 5),
    },
  ];

  return (
    <>
      <div className="grid grid-cols-3 gap-4 bg-[#00783440] text-[#007834] h-[100vh]">
        <div className="col-span-2 margin-1 m-3 rounded-xl bg-neutral-100 max-h-full overflow-auto">
          <Routes>
            <Route path="/" element={<VictimExplanationForm />} />
          </Routes>
        </div>
        <div className="margin-1 m-3 rounded-xl bg-neutral-100 max-h-full overflow-auto relative">
          <ChatWidget initialMessages={initialHistory} />
          {/* <div className="absolute top-4 right-4 cursor-pointer hover:text-primary transition duration-150 ease-in-out border-2 border-primary rounded-xl p-1">
            <ArrowLeft size={25}/>
          </div> */}
        </div>
      </div>
    </>
  );
};

export { App };
