import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  FormControlLabel,
  Switch,
  Slider,
  Grid,
  Autocomplete,
  CircularProgress,
  Alert,
  Stack,
  Divider,
} from '@mui/material';
import { createTask, createAndAssignTask, getTasks } from '../api/api';

export default function NewTask() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState(5);
  const [deadlineDays, setDeadlineDays] = useState<number | null>(null);
  const [requiredSkills, setRequiredSkills] = useState<string[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [estimatedHours, setEstimatedHours] = useState<number | undefined>(undefined);
  const [dependencyIds, setDependencyIds] = useState<number[]>([]);
  const [skillInput, setSkillInput] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [autoAssign, setAutoAssign] = useState(false);

  // Get existing tasks for dependency selection
  const { data: existingTasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: getTasks,
  });

  // Create task mutation
  const createTaskMutation = useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['organization'] });
      navigate('/tasks');
    },
  });

  // Create and assign task mutation
  const createAndAssignTaskMutation = useMutation({
    mutationFn: createAndAssignTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['workers'] });
      queryClient.invalidateQueries({ queryKey: ['organization'] });
      navigate('/tasks');
    },
  });

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    
    const taskData = {
      title,
      description,
      priority,
      deadline_days: deadlineDays,
      required_skills: requiredSkills,
      tags,
      estimated_hours: estimatedHours,
      dependency_ids: dependencyIds,
    };
    
    if (autoAssign) {
      createAndAssignTaskMutation.mutate(taskData);
    } else {
      createTaskMutation.mutate(taskData);
    }
  };

  const handleAddSkill = () => {
    if (skillInput && !requiredSkills.includes(skillInput)) {
      setRequiredSkills([...requiredSkills, skillInput]);
      setSkillInput('');
    }
  };

  const handleAddTag = () => {
    if (tagInput && !tags.includes(tagInput)) {
      setTags([...tags, tagInput]);
      setTagInput('');
    }
  };

  const handleRemoveSkill = (skill: string) => {
    setRequiredSkills(requiredSkills.filter(s => s !== skill));
  };

  const handleRemoveTag = (tag: string) => {
    setTags(tags.filter(t => t !== tag));
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Create New Task
      </Typography>

      <Paper sx={{ p: 3, mt: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* Basic task information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                fullWidth
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                multiline
                rows={4}
                fullWidth
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Priority (1-10)</Typography>
              <Slider
                value={priority}
                onChange={(_, newValue) => setPriority(newValue as number)}
                step={1}
                marks
                min={1}
                max={10}
                valueLabelDisplay="auto"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                label="Deadline (days from now)"
                type="number"
                value={deadlineDays === null ? '' : deadlineDays}
                onChange={(e) => {
                  const value = e.target.value === '' ? null : Number(e.target.value);
                  setDeadlineDays(value);
                }}
                InputProps={{ inputProps: { min: 1 } }}
                fullWidth
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                label="Estimated Hours"
                type="number"
                value={estimatedHours === undefined ? '' : estimatedHours}
                onChange={(e) => {
                  const value = e.target.value === '' ? undefined : Number(e.target.value);
                  setEstimatedHours(value);
                }}
                InputProps={{ inputProps: { min: 0, step: 0.5 } }}
                fullWidth
              />
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
            </Grid>
            
            {/* Skills and tags section */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Skills and Tags
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Box sx={{ mb: 2 }}>
                <TextField
                  label="Required Skills"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  fullWidth
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddSkill();
                    }
                  }}
                />
                <Button 
                  variant="outlined" 
                  onClick={handleAddSkill} 
                  sx={{ mt: 1 }}
                  size="small"
                >
                  Add Skill
                </Button>
              </Box>
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {requiredSkills.map((skill, index) => (
                  <Chip
                    key={index}
                    label={skill}
                    onDelete={() => handleRemoveSkill(skill)}
                  />
                ))}
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Box sx={{ mb: 2 }}>
                <TextField
                  label="Tags"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  fullWidth
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddTag();
                    }
                  }}
                />
                <Button 
                  variant="outlined" 
                  onClick={handleAddTag} 
                  sx={{ mt: 1 }}
                  size="small"
                >
                  Add Tag
                </Button>
              </Box>
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {tags.map((tag, index) => (
                  <Chip
                    key={index}
                    label={tag}
                    variant="outlined"
                    onDelete={() => handleRemoveTag(tag)}
                  />
                ))}
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
            </Grid>
            
            {/* Dependencies */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Dependencies
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              {tasksLoading ? (
                <CircularProgress size={24} />
              ) : (
                <Autocomplete
                  multiple
                  options={existingTasks || []}
                  getOptionLabel={(option) => option.title}
                  onChange={(_, newValue) => {
                    setDependencyIds(newValue.map((task, index) => index));
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Task Dependencies"
                      placeholder="Select dependencies"
                    />
                  )}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip
                        label={option.title}
                        {...getTagProps({ index })}
                        key={index}
                      />
                    ))
                  }
                />
              )}
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
            </Grid>
            
            {/* Auto-assign option */}
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={autoAssign}
                    onChange={(e) => setAutoAssign(e.target.checked)}
                  />
                }
                label="Auto-assign task to most suitable worker"
              />
            </Grid>
            
            {/* Submit buttons */}
            <Grid item xs={12}>
              <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
                <Button 
                  variant="contained" 
                  color="primary" 
                  type="submit"
                  disabled={
                    createTaskMutation.isPending || 
                    createAndAssignTaskMutation.isPending ||
                    !title || 
                    !description
                  }
                >
                  {createTaskMutation.isPending || createAndAssignTaskMutation.isPending ? 
                    'Creating...' : 'Create Task'
                  }
                </Button>
                <Button 
                  variant="outlined" 
                  onClick={() => navigate('/tasks')}
                >
                  Cancel
                </Button>
              </Stack>
            </Grid>
            
            {/* Error message */}
            {(createTaskMutation.error || createAndAssignTaskMutation.error) && (
              <Grid item xs={12}>
                <Alert severity="error">
                  Error creating task. Please try again.
                </Alert>
              </Grid>
            )}
          </Grid>
        </form>
      </Paper>
    </Box>
  );
}