import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  FormControlLabel,
  Switch,
  Grid,
  Chip,
  Alert,
  Stack,
  Divider,
} from '@mui/material';
import { createWorker } from '../api/api';

export default function NewWorker() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [name, setName] = useState('');
  const [isHuman, setIsHuman] = useState(true);
  const [skills, setSkills] = useState<string[]>([]);
  const [experienceDescription, setExperienceDescription] = useState('');
  const [skillInput, setSkillInput] = useState('');

  // Create worker mutation
  const createWorkerMutation = useMutation({
    mutationFn: createWorker,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workers'] });
      queryClient.invalidateQueries({ queryKey: ['organization'] });
      navigate('/workers');
    },
  });

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    
    const workerData = {
      name,
      is_human: isHuman,
      skills,
      experience_description: experienceDescription,
    };
    
    createWorkerMutation.mutate(workerData);
  };

  const handleAddSkill = () => {
    if (skillInput && !skills.includes(skillInput)) {
      setSkills([...skills, skillInput]);
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (skill: string) => {
    setSkills(skills.filter(s => s !== skill));
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Add New Worker
      </Typography>

      <Paper sx={{ p: 3, mt: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* Basic worker information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                fullWidth
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={isHuman}
                    onChange={(e) => setIsHuman(e.target.checked)}
                    color="primary"
                  />
                }
                label={isHuman ? "Human Worker" : "AI Assistant"}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
            </Grid>
            
            {/* Skills */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Skills
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <Box sx={{ mb: 2 }}>
                <TextField
                  label="Skills"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  fullWidth
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddSkill();
                    }
                  }}
                  helperText="Press Enter to add a skill"
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
                {skills.map((skill, index) => (
                  <Chip
                    key={index}
                    label={skill}
                    onDelete={() => handleRemoveSkill(skill)}
                  />
                ))}
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
            </Grid>
            
            {/* Experience */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Experience (Optional)
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="Experience Description"
                value={experienceDescription}
                onChange={(e) => setExperienceDescription(e.target.value)}
                multiline
                rows={6}
                fullWidth
                placeholder="Describe the worker's previous experience, skills proficiency, areas of expertise, etc."
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
                    createWorkerMutation.isPending ||
                    !name || 
                    skills.length === 0
                  }
                >
                  {createWorkerMutation.isPending ? 'Creating...' : 'Add Worker'}
                </Button>
                <Button 
                  variant="outlined" 
                  onClick={() => navigate('/workers')}
                >
                  Cancel
                </Button>
              </Stack>
            </Grid>
            
            {/* Error message */}
            {createWorkerMutation.error && (
              <Grid item xs={12}>
                <Alert severity="error">
                  Error creating worker. Please try again.
                </Alert>
              </Grid>
            )}
          </Grid>
        </form>
      </Paper>
    </Box>
  );
}