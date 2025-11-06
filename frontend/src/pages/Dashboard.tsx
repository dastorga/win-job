import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  FormControlLabel,
  Checkbox,
  CircularProgress,
  Chip,
  Box,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { Search, Work, FilterList, Refresh } from '@mui/icons-material';
import { jobsAPI } from '../services/api';
import { Job, JobStats, ScrapeResponse } from '../types';

const Dashboard: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState<JobStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  
  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [noEnglish, setNoEnglish] = useState(true);
  const [companyFilter, setCompanyFilter] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  
  // Scraping dialog state
  const [scrapeDialogOpen, setScrapeDialogOpen] = useState(false);
  const [scrapeParams, setScrapeParams] = useState({
    search_term: 'DevOps',
    location: 'España',
    max_jobs: 50,
  });

  useEffect(() => {
    loadJobs();
    loadStats();
  }, [searchTerm, noEnglish, companyFilter, locationFilter]);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const jobsData = await jobsAPI.getJobs({
        search: searchTerm || undefined,
        no_english: noEnglish,
        company: companyFilter || undefined,
        location: locationFilter || undefined,
        limit: 50,
      });
      setJobs(jobsData);
    } catch (err) {
      setError('Error loading jobs');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const statsData = await jobsAPI.getJobStats();
      setStats(statsData);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const handleScrapeJobs = async () => {
    setScraping(true);
    try {
      const result: ScrapeResponse = await jobsAPI.scrapeJobs(scrapeParams);
      setSuccess(result.message);
      setScrapeDialogOpen(false);
      // Reload jobs and stats
      await loadJobs();
      await loadStats();
    } catch (err) {
      setError('Error scraping jobs');
    } finally {
      setScraping(false);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Fecha no disponible';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <>
      <AppBar position="static" sx={{ mb: 3 }}>
        <Toolbar>
          <Work sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            DevOps Job Scraper
          </Typography>
          <Button
            color="inherit"
            startIcon={<Refresh />}
            onClick={() => setScrapeDialogOpen(true)}
          >
            Buscar Ofertas
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg">
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        {/* Stats Cards */}
        {stats && (
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Ofertas
                  </Typography>
                  <Typography variant="h4">
                    {stats.total_jobs}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Sin Inglés
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {stats.jobs_without_english}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    % Con Inglés
                  </Typography>
                  <Typography variant="h4" color="error">
                    {stats.english_percentage}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Empresas
                  </Typography>
                  <Typography variant="h4">
                    {stats.top_companies.length}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Filters */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <FilterList sx={{ mr: 1 }} />
              Filtros
            </Typography>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  placeholder="Buscar por título..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: <Search sx={{ mr: 1 }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  placeholder="Empresa..."
                  value={companyFilter}
                  onChange={(e) => setCompanyFilter(e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  placeholder="Ubicación..."
                  value={locationFilter}
                  onChange={(e) => setLocationFilter(e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={noEnglish}
                      onChange={(e) => setNoEnglish(e.target.checked)}
                    />
                  }
                  label="Solo sin inglés"
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Jobs List */}
        {loading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={2}>
            {jobs.map((job) => (
              <Grid item xs={12} key={job.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                      <Box>
                        <Typography variant="h6" component="h2">
                          {job.title}
                        </Typography>
                        <Typography color="textSecondary" variant="subtitle1">
                          {job.company} • {job.location}
                        </Typography>
                      </Box>
                      <Box>
                        {!job.requires_english && (
                          <Chip label="Sin inglés" color="success" size="small" sx={{ mr: 1 }} />
                        )}
                        {job.employment_type && (
                          <Chip label={job.employment_type} variant="outlined" size="small" />
                        )}
                      </Box>
                    </Box>
                    
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {job.description.length > 300 
                        ? `${job.description.substring(0, 300)}...` 
                        : job.description
                      }
                    </Typography>
                    
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="body2" color="textSecondary">
                        Publicado: {formatDate(job.posted_date)}
                      </Typography>
                      <Button
                        variant="contained"
                        size="small"
                        onClick={() => window.open(job.linkedin_url, '_blank')}
                      >
                        Ver en LinkedIn
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
            
            {jobs.length === 0 && !loading && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" align="center" color="textSecondary">
                      No se encontraron ofertas con los filtros actuales
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        )}
      </Container>

      {/* Scrape Dialog */}
      <Dialog open={scrapeDialogOpen} onClose={() => setScrapeDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Buscar nuevas ofertas en LinkedIn</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Término de búsqueda"
                value={scrapeParams.search_term}
                onChange={(e) => setScrapeParams({...scrapeParams, search_term: e.target.value})}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Ubicación"
                value={scrapeParams.location}
                onChange={(e) => setScrapeParams({...scrapeParams, location: e.target.value})}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Máximo de ofertas"
                type="number"
                value={scrapeParams.max_jobs}
                onChange={(e) => setScrapeParams({...scrapeParams, max_jobs: parseInt(e.target.value)})}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScrapeDialogOpen(false)}>Cancelar</Button>
          <Button 
            onClick={handleScrapeJobs} 
            variant="contained" 
            disabled={scraping}
            startIcon={scraping ? <CircularProgress size={20} /> : <Search />}
          >
            {scraping ? 'Buscando...' : 'Buscar Ofertas'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default Dashboard;