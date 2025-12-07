import { Route, Routes, useLocation } from 'react-router-dom';

import { VictimExplanationForm } from '@/pages';
import { Message } from '@/types';
import { ChatWidget } from './ChatWidget';
import { useCtx } from '@/context';
import { Home } from '@/pages/Home';
import { AccidentReportForm } from '@/pages/AccidentReportForm';

const App = () => {
  const ctx = useCtx();
  const chatHistory: Message[] = [];

  const route = useLocation();
  const showChatWidget = route.pathname !== '/';

  return (
    <>
      <div className="grid grid-cols-3 bg-[#00783440] text-[#007834] h-[100vh]">
        <div className={`${showChatWidget ? "col-span-2" : "col-span-3"}
      margin-1 m-3 rounded-xl bg-neutral-100 max-h-full overflow-auto`}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/report" element={<VictimExplanationForm />} />
            <Route path="/statement" element={<AccidentReportForm />} />
          </Routes>
        </div>
        {showChatWidget && (
          <div className="margin-1 m-3 rounded-xl bg-neutral-100 max-h-full overflow-auto relative">
            <ChatWidget
              initialMessages={chatHistory}
              onCollectedData={collectedData => ctx.setCollectedData(collectedData)}
            />
          </div>
        )}
      </div>
    </>
  );
};

export { App };
