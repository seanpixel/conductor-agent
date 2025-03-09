import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Button,
  Paper,
  Box,
  Divider,
  Chip,
  CircularProgress,
  Alert,
  useTheme,
} from '@mui/material';
import { 
  Assignment as AssignIcon,
  People as PeopleIcon,
  AssignmentTurnedIn as CompletedIcon,
  AssignmentLate as PendingIcon,
  Work as WorkIcon
} from '@mui/icons-material';
import { getOrganization, getOrganizationState, assignAllTasks } from '../api/api';
import { commonStyles } from '../styles/common';

export default function Dashboard() {
  const [assigning, setAssigning] = useState(false);
  
  const { 
    data: orgData, 
    isLoading: orgLoading, 
    error: orgError,
    refetch: refetchOrg
  } = useQuery({
    queryKey: ['organization'],
    queryFn: getOrganization,
  });

  const { 
    data: orgStateData, 
    isLoading: stateLoading, 
    error: stateError,
    refetch: refetchState
  } = useQuery({
    queryKey: ['organizationState'],
    queryFn: getOrganizationState,
  });

  const handleAssignTasks = async () => {
    try {
      setAssigning(true);
      await assignAllTasks();
      // Refetch data after assignment
      await refetchOrg();
      await refetchState();
    } catch (error) {
      console.error('Error assigning tasks:', error);
    } finally {
      setAssigning(false);
    }
  };

  if (orgLoading || stateLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (orgError || stateError) {
    return (
      <Alert severity="error">
        Error loading organization data. Please try again.
      </Alert>
    );
  }

  const unassignedTasks = orgData?.tasks?.filter(task => !task.assigned_worker) || [];
  const assignedTasks = orgData?.tasks?.filter(task => task.assigned_worker) || [];
  const completedTasks = orgData?.completed_tasks || [];

  const theme = useTheme();
  
  return (
    <Box sx={commonStyles.pageContainer}>
      <Box sx={{ 
        mb: 4, 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        borderBottom: `1px solid ${theme.palette.divider}`,
        pb: 2,
        width: '100%'
      }}>
        <Typography variant="h4" component="h1" sx={{ 
          fontWeight: 600,
          position: 'relative',
          '&:after': {
            content: '""',
            position: 'absolute',
            bottom: -12,
            left: 0,
            width: 100,
            height: 4,
            borderRadius: 2,
            backgroundColor: theme.palette.primary.main,
          }
        }}>
          {orgData?.name || 'Organization'} Dashboard
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleAssignTasks}
          disabled={assigning || unassignedTasks.length === 0}
          startIcon={<AssignIcon />}
          sx={{ 
            px: 3, 
            py: 1,
            borderRadius: 2,
            boxShadow: 2,
            fontWeight: 600,
            '&:hover': {
              boxShadow: 4,
            }
          }}
        >
          {assigning ? 'Assigning...' : 'Assign Tasks'}
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ 
              borderRadius: 2,
              boxShadow: 2,
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 4,
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: 'rgba(63, 81, 181, 0.1)',
                    mr: 2
                  }}
                >
                  <PeopleIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />
                </Box>
                <Typography sx={{ fontWeight: 600, fontSize: '1.1rem', color: 'text.secondary' }}>
                  Workers
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                {orgData?.workers?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ 
              borderRadius: 2,
              boxShadow: 2,
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 4,
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    mr: 2
                  }}
                >
                  <WorkIcon sx={{ color: theme.palette.info.main, fontSize: 28 }} />
                </Box>
                <Typography sx={{ fontWeight: 600, fontSize: '1.1rem', color: 'text.secondary' }}>
                  Active Tasks
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 700 }}>
                {orgData?.tasks?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ 
              borderRadius: 2,
              boxShadow: 2,
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 4,
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: unassignedTasks.length > 0 ? 'rgba(244, 67, 54, 0.1)' : 'rgba(158, 158, 158, 0.1)',
                    mr: 2
                  }}
                >
                  <PendingIcon sx={{ 
                    color: unassignedTasks.length > 0 ? theme.palette.error.main : theme.palette.text.secondary, 
                    fontSize: 28 
                  }} />
                </Box>
                <Typography sx={{ fontWeight: 600, fontSize: '1.1rem', color: 'text.secondary' }}>
                  Unassigned
                </Typography>
              </Box>
              <Typography 
                variant="h3" 
                sx={{ 
                  fontWeight: 700,
                  color: unassignedTasks.length > 0 ? "error.main" : "inherit"
                }}
              >
                {unassignedTasks.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card 
            sx={{ 
              borderRadius: 2,
              boxShadow: 2,
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 4,
              }
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    mr: 2
                  }}
                >
                  <CompletedIcon sx={{ color: theme.palette.success.main, fontSize: 28 }} />
                </Box>
                <Typography sx={{ fontWeight: 600, fontSize: '1.1rem', color: 'text.secondary' }}>
                  Completed
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 700, color: "success.main" }}>
                {completedTasks.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Organization State */}
        <Grid item xs={12}>
          <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
            <CardHeader 
              title={
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Organization State
                </Typography>
              }
              sx={{ 
                borderBottom: `1px solid ${theme.palette.divider}`,
                backgroundColor: 'rgba(0, 0, 0, 0.02)'
              }}
            />
            <CardContent sx={{ p: 0 }}>
              <Paper 
                elevation={0} 
                sx={{ 
                  p: 3, 
                  bgcolor: 'background.default', 
                  maxHeight: '400px', 
                  overflow: 'auto',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  fontSize: '0.9rem',
                  lineHeight: 1.6,
                  borderRadius: 0
                }}
              >
                {orgStateData?.organization_state || 'No organization state data available.'}
              </Paper>
            </CardContent>
          </Card>
        </Grid>

        {/* Workers Overview */}
        <Grid item xs={12} md={6}>
          <Card sx={{ 
            borderRadius: 2, 
            boxShadow: 2,
            height: '100%',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <CardHeader 
              title={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <PeopleIcon sx={{ mr: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Workers
                  </Typography>
                </Box>
              }
              sx={{ 
                borderBottom: `1px solid ${theme.palette.divider}`,
                backgroundColor: 'rgba(0, 0, 0, 0.02)'
              }}
            />
            <CardContent sx={{ p: 2, flexGrow: 1, overflow: 'auto', maxHeight: '400px' }}>
              {Array.isArray(orgData?.workers) && orgData?.workers.length > 0 ? (
                orgData.workers.map((worker, index) => (
                  <Box 
                    key={index} 
                    sx={{ 
                      mb: 2, 
                      p: 2, 
                      borderRadius: 2, 
                      bgcolor: 'background.paper',
                      boxShadow: 1,
                      transition: 'transform 0.2s',
                      '&:hover': {
                        transform: 'translateX(4px)',
                        boxShadow: 2
                      },
                      border: `1px solid ${theme.palette.divider}`,
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1, alignItems: 'center' }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {worker.name}
                      </Typography>
                      <Chip 
                        label={worker.is_human ? 'Human' : 'AI'} 
                        size="small" 
                        color={worker.is_human ? 'primary' : 'secondary'} 
                        sx={{ fontWeight: 500 }}
                      />
                    </Box>
                    <Box sx={commonStyles.skillsContainer}>
                      {worker.skills.map((skill: string, idx: number) => (
                        <Chip 
                          key={idx} 
                          label={skill} 
                          size="small" 
                          variant="outlined" 
                          sx={{ 
                            borderRadius: '4px',
                            '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.04)' }
                          }}
                        />
                      ))}
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center' }}>
                        <WorkIcon sx={{ fontSize: '0.9rem', mr: 0.5, color: 'primary.main' }} />
                        {worker.assigned_tasks.length} active
                      </Typography>
                      <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center' }}>
                        <CompletedIcon sx={{ fontSize: '0.9rem', mr: 0.5, color: 'success.main' }} />
                        {worker.completed_tasks.length} completed
                      </Typography>
                      <Chip 
                        label={`Workload: ${worker.workload.toFixed(1)}`} 
                        size="small"
                        color={
                          worker.workload > 7 ? 'error' :
                          worker.workload > 3 ? 'warning' :
                          'success'
                        }
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                ))
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No workers available yet
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Tasks */}
        <Grid item xs={12} md={6}>
          <Card sx={{ 
            borderRadius: 2, 
            boxShadow: 2,
            height: '100%',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <CardHeader 
              title={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <WorkIcon sx={{ mr: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Recent Tasks
                  </Typography>
                </Box>
              }
              sx={{ 
                borderBottom: `1px solid ${theme.palette.divider}`,
                backgroundColor: 'rgba(0, 0, 0, 0.02)'
              }}
            />
            <CardContent sx={{ p: 2, flexGrow: 1, overflow: 'auto', maxHeight: '400px' }}>
              {[...assignedTasks, ...unassignedTasks].length > 0 ? (
                [...assignedTasks, ...unassignedTasks].slice(0, 5).map((task, index) => (
                  <Box 
                    key={index} 
                    sx={{ 
                      mb: 2, 
                      p: 2, 
                      borderRadius: 2, 
                      bgcolor: 'background.paper',
                      boxShadow: 1,
                      transition: 'transform 0.2s',
                      '&:hover': {
                        transform: 'translateX(4px)',
                        boxShadow: 2
                      },
                      border: `1px solid ${theme.palette.divider}`,
                      borderLeft: '4px solid',
                      borderLeftColor: task.priority >= 8 ? 'error.main' : (task.priority >= 5 ? 'warning.main' : 'success.main')
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1, alignItems: 'center' }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {task.title}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Chip 
                          label={`P${task.priority}`} 
                          size="small" 
                          color={task.priority >= 8 ? 'error' : task.priority >= 5 ? 'warning' : 'success'} 
                          sx={{ fontWeight: 'bold' }}
                        />
                        <Chip 
                          label={task.status} 
                          size="small" 
                          color={
                            task.status === 'completed' ? 'success' : 
                            task.status === 'in_progress' ? 'info' : 
                            task.status === 'blocked' ? 'error' : 
                            'default'
                          } 
                          sx={{ textTransform: 'capitalize' }}
                        />
                      </Box>
                    </Box>
                    <Typography 
                      variant="body2" 
                      color="text.secondary" 
                      sx={{ 
                        mb: 1,
                        display: '-webkit-box',
                        overflow: 'hidden',
                        WebkitBoxOrient: 'vertical',
                        WebkitLineClamp: 2,
                        lineHeight: 1.5,
                        height: '3em'
                      }}
                    >
                      {task.description}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      {task.assigned_worker ? (
                        <Chip
                          label={task.assigned_worker}
                          size="small"
                          color="primary"
                          variant="outlined"
                          sx={{ fontWeight: 500 }}
                        />
                      ) : (
                        <Chip
                          label="Unassigned"
                          size="small"
                          variant="outlined"
                          sx={{ fontStyle: 'italic' }}
                        />
                      )}
                      {task.deadline && (
                        <Typography variant="caption" color="text.secondary">
                          Due: {new Date(task.deadline).toLocaleDateString()}
                        </Typography>
                      )}
                    </Box>
                  </Box>
                ))
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No tasks available yet
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}