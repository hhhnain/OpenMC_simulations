#!/usr/bin/env python
# coding: utf-8

# In[82]:


import openmc
import openmc.mgxs
import matplotlib.pyplot as plt
import time
import numpy as np


# In[79]:


#create material, #define fuel,clad,moderator etc
#geometry by making surface, then cells, then universe then geometry
#setting files with source, particles, etc
#creates tallies, or mgxs
time1 = time.time()


# In[18]:


fuel = openmc.Material(1,'uo2')
fuel.add_nuclide('U235',0.1)
fuel.add_nuclide('U238',0.9)
fuel.add_nuclide('O16',2)
fuel.set_density('g/cm3',10.97)
mats = openmc.Materials([fuel])
mats.export_to_xml()


# In[19]:


#surface
a = 70
left = openmc.XPlane(x0=-a,boundary_type='vacuum')
right = openmc.XPlane(x0=a,boundary_type='vacuum')
front = openmc.YPlane(y0=-a,boundary_type='vacuum')
back = openmc.YPlane(y0=a,boundary_type='vacuum')
top = openmc.ZPlane(z0=a,boundary_type='vacuum')
bottom = openmc.ZPlane(z0=-a,boundary_type='vacuum')


# In[20]:


#cell
slab_cell = openmc.Cell()
slab_cell.region = +left & -right & +bottom & -top #& +front & -back 
slab_cell.fill = fuel


# In[21]:


#univers
universe = openmc.Universe(cells=[slab_cell])
#geometry
slab_geometry = openmc.Geometry()
slab_geometry.root_universe = universe
slab_geometry.export_to_xml()


# In[22]:


universe.plot(width=(180,180))


# In[73]:


batches = 250
particles = 1000000
inactive = 100
settings = openmc.Settings()
settings.particles = particles
settings.batches = batches
settings.inactive = inactive
#settings.energy_mode = 'multi-group'
bounds = [-a,-a,-a,a,a,a]
uniform_dist = openmc.stats.Box(
    lower_left = bounds[:3],
    upper_right=bounds[3:],
    only_fissionable=True
)
settings.source = openmc.Source(space=uniform_dist)
settings.export_to_xml()


# In[24]:


energy_filter = openmc.EnergyFilter([0,1000,20e6])
#energy_filter = openmc.EnergyFilter([0,20e6])


# In[25]:


mesh = openmc.RegularMesh()
mesh.dimension = 140,1,1
mesh.lower_left = bounds[:3]
mesh.upper_right = bounds[3:]


# In[26]:


mesh_filter = openmc.MeshFilter(mesh=mesh)


# In[27]:


tallies_file = openmc.Tallies()
tally = openmc.Tally(name='flux')
tally.filters = [mesh_filter,energy_filter]
tally.scores = ['flux']
tallies_file.append(tally)
tallies_file.export_to_xml()


# In[13]:


openmc.run()


# In[75]:


sp = openmc.StatePoint(f'statepoint.{batches}.h5')


# In[33]:


flux_rate = sp.get_tally(scores=['flux'],filters=[energy_filter])


# In[66]:


group_1 = flux_rate.mean[::2].reshape(-1)
group_2 = flux_rate.mean[1::2].reshape(-1)


# In[68]:


#plt.plot(group_2)
plt.plot(group_1)


# In[70]:


plt.plot(group_2)


# In[84]:


print(np.array([group_1]))
print(np.array([group_2]))
time2 = time.time()
tot_time = time2 - time1 
print(f'time for simulation: {tot_time} secs')


# In[ ]:




