/**
 * Common styles for consistent UI across components
 */
import { Theme } from '@mui/material/styles';

export const commonStyles = {
  // Page container styling
  pageContainer: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: 3,
  },
  
  // Section styling
  section: {
    marginBottom: 4,
  },
  
  // Card styling
  card: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    transition: 'all 0.2s ease-in-out',
    '&:hover': {
      transform: 'translateY(-4px)',
      boxShadow: (theme: Theme) => theme.shadows[4],
    },
  },
  
  cardHeader: {
    paddingBottom: 1,
  },
  
  cardContent: {
    paddingTop: 1,
    flexGrow: 1,
    display: 'flex',
    flexDirection: 'column',
  },
  
  // Centering containers for tasks and workers
  centerContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
  },
  
  // Workers container with centered grid layout
  workersContainer: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    maxWidth: '1200px',
  },
  
  // Tasks container with centered content
  tasksContainer: {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    maxWidth: '1200px',
  },
  
  // Table styling
  table: {
    '& .MuiTableCell-head': {
      fontWeight: 'bold',
      backgroundColor: (theme: Theme) => theme.palette.primary.main,
      color: '#fff',
    },
    '& .MuiTableRow-root:nth-of-type(even)': {
      backgroundColor: (theme: Theme) => theme.palette.action.hover,
    },
    '& .MuiTableCell-root': {
      padding: '12px 16px',
    },
  },
  
  // Typography styling
  sectionTitle: {
    marginBottom: 2,
    position: 'relative',
    paddingBottom: 1,
    alignSelf: 'flex-start',
    '&:after': {
      content: '""',
      position: 'absolute',
      bottom: 0,
      left: 0,
      width: '50px',
      height: '3px',
      backgroundColor: (theme: Theme) => theme.palette.primary.main,
    },
  },
  
  // Grid item styling for equal height cards
  gridItem: {
    display: 'flex',
    '& > *': {
      width: '100%',
    },
  },
  
  // Skills chip container
  skillsContainer: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 0.5,
    marginBottom: 2,
  },
  
  // Info section in cards
  infoSection: {
    marginBottom: 2,
  },
  
  // Priority indicator styling
  priorityIndicator: {
    width: 12,
    height: 12,
    borderRadius: '50%',
    display: 'inline-block',
    marginRight: 1,
  },
  
  // Task list styling
  taskList: {
    padding: 0,
    margin: 0,
    listStyle: 'none',
    '& li': {
      padding: '6px 0',
      borderBottom: '1px solid #eee',
      '&:last-child': {
        borderBottom: 'none',
      },
    },
  },
};