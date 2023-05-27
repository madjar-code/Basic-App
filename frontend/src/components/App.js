import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from 'react-router-dom'

import { UserProvider } from "../providers/UserContext";
import { ProtectedRoute, NoAuthRoute } from "../routes";
import Terms from "./Terms";


const App = () => {
  return (
    <Router>
      <UserProvider>
        <Routes>
          <Route path="/terms" element={<Terms/>} />
        </Routes>
      </UserProvider>
    </Router>
  );
};

export default App;