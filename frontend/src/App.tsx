import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Components
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Workers from './pages/Workers';
import NewTask from './pages/NewTask';
import NewWorker from './pages/NewWorker';

// Create a theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
  },
});

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  // Log environment information on app startup
  console.log('App startup: Environment information');
  console.log('Current URL:', window.location.href);
  console.log('Hostname:', window.location.hostname);
  console.log('Protocol:', window.location.protocol);
  console.log('Port:', window.location.port);
  console.log('Is running in GitHub Codespaces:', 
    window.location.hostname.includes('github.dev') || 
    window.location.hostname.includes('codespaces') ||
    window.location.hostname.includes('app.github.dev')
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Box sx={{ display: 'flex' }}>
            <Navbar />
            <Box 
              component="main" 
              sx={{ 
                flexGrow: 1, 
                p: 3, 
                mt: 8,
              }}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/tasks" element={<Tasks />} />
                <Route path="/workers" element={<Workers />} />
                <Route path="/new-task" element={<NewTask />} />
                <Route path="/new-worker" element={<NewWorker />} />
              </Routes>
            </Box>
          </Box>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
