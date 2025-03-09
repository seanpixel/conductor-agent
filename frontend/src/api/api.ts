import axios from 'axios';

// Determine API URL based on environment
// For GitHub Codespaces, we need to use an API proxy approach to avoid CORS issues
const isCodespace = window.location.hostname.includes('github.dev') || 
                    window.location.hostname.includes('githubpreview') ||
                    window.location.hostname.includes('codespaces') ||
                    window.location.hostname.includes('app.github.dev');

// For Codespaces: use a relative URL to the backend service
// The proxy is handled by the GitHub Codespaces infrastructure
let API_URL = isCodespace ? '/api' : 'http://localhost:8080';

console.log('Using API URL:', API_URL);

console.log('API URL configured as:', API_URL || 'Using relative URLs for Codespace environment');

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Organization
export const getOrganization = async () => {
  try {
    console.log('Fetching organization data...');
    const response = await api.get('/organization');
    console.log('Organization API response:', response);
    return response.data;
  } catch (error) {
    console.error('Error in getOrganization:', error);
    console.error('API URL being used:', API_URL);
    return {
      name: 'Error',
      workers: [],
      tasks: [],
      completed_tasks: []
    };
  }
};

export const getOrganizationState = async () => {
  try {
    console.log('Fetching organization state...');
    const response = await api.get('/organization-state');
    console.log('Organization state API response:', response);
    return response.data;
  } catch (error) {
    console.error('Error in getOrganizationState:', error);
    return { organization_state: 'Error loading organization state' };
  }
};

// Workers
export const getWorkers = async () => {
  try {
    const response = await api.get('/workers');
    console.log('getWorkers API response:', response);
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('Error in getWorkers:', error);
    return [];
  }
};

export const getWorker = async (workerId: number) => {
  const response = await api.get(`/workers/${workerId}`);
  return response.data;
};

export const createWorker = async (workerData: any) => {
  const response = await api.post('/workers', workerData);
  return response.data;
};

// Tasks
export const getTasks = async () => {
  try {
    const response = await api.get('/tasks');
    console.log('getTasks API response:', response);
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('Error in getTasks:', error);
    return [];
  }
};

export const getTask = async (taskId: number) => {
  try {
    const response = await api.get(`/tasks/${taskId}`);
    return response.data;
  } catch (error) {
    console.error(`Error in getTask(${taskId}):`, error);
    throw error;
  }
};

export const createTask = async (taskData: any) => {
  try {
    const response = await api.post('/tasks', taskData);
    return response.data;
  } catch (error) {
    console.error('Error in createTask:', error);
    throw error;
  }
};

export const createAndAssignTask = async (taskData: any) => {
  try {
    const response = await api.post('/tasks/new-assign', taskData);
    return response.data;
  } catch (error) {
    console.error('Error in createAndAssignTask:', error);
    throw error;
  }
};

export const assignTask = async (taskId: number, workerName: string) => {
  try {
    const response = await api.post(`/tasks/${taskId}/assign`, { worker_name: workerName });
    return response.data;
  } catch (error) {
    console.error(`Error in assignTask(${taskId}, ${workerName}):`, error);
    throw error;
  }
};

export const assignAllTasks = async () => {
  try {
    const response = await api.post('/tasks/assign');
    return response.data;
  } catch (error) {
    console.error('Error in assignAllTasks:', error);
    throw error;
  }
};

export const completeTask = async (taskId: number, feedback?: string) => {
  try {
    const response = await api.post(`/tasks/${taskId}/complete`, { feedback });
    return response.data;
  } catch (error) {
    console.error(`Error in completeTask(${taskId}):`, error);
    throw error;
  }
};

export const getCompletedTasks = async () => {
  try {
    const response = await api.get('/completed-tasks');
    console.log('getCompletedTasks API response:', response);
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('Error in getCompletedTasks:', error);
    return [];
  }
};

export default api;