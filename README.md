# mHouse Cloud Platform Component
The mHouse Framework Cloud Platform component.

# General Description
<img src="https://github.com/JRequeijo/mHouseFramework/blob/master/docs/Cloud%20Platform/Cloud_platform_arch.png" alt="Cloud Platform Architecture">
<p>
The Cloud Platform component prototype is a cloud-based web application constructed with the Django Framework which can be accessed on http://mhouseframework.eu-west-1.elasticbeanstalk.com/. As presented on Figure 24, it is composed by a web server, which holds all the application logic, an Object-Relational Mapping (ORM) Module that provides an Object-like interface to a SQL Database which, in turn, is the final subcomponent and is where the overall framework’s data is stored.
</p>

<p>
On the web server, besides the module that handles all incoming requests, there are also two modules that monitor, respectively, all the Home Servers and all Devices registered on the Cloud Plat- form. These monitoring modules are always running in parallel with the remaining application, each one in its specific thread, where the correspondent monitoring function works by periodically comparing the current timestamp with the timestamp of the last access done by a Home Server or a Device (depending on the monitor module), plus a specific ”timeout” characteristic of each Home Server and/or Device. Therefore, when a Home Server or a Device does not send any request to the Cloud Platform (does not access it) during a time interval greater than the “timeout” value, these monitoring modules consider that the correspondent Home Server or Device is “down”, and they accordingly change its correspon- dent state. This mechanism provides a simple way to always detect Home Server or Device failures, even when the user is not using (accessing) the Cloud Platform, which is relevant to allow, for example, alarmistic services which can use this information to alert the user in case of failures or emergency situations.
</p>

<p>
The SQL database stores all the relevant information about the mHouse Framework and, when working normally, it is always synchronized with all registered Home Servers. It stores all the data representations for each User,House, Area, Division, Home Server, Device, Configuration, Service, User Action and Device State Update/Change, that is created/registered on the Cloud Platform. All this information is modulated as explained on section 3.3 to allow its correct storage and management on a common relational SQL database.
</p>

<p>
For more detailed information check <a href="https://github.com/JRequeijo/mHouseFramework/tree/master/docs/Cloud%20Platform">Cloud Platform Official Documentation</a>.
</p>

# Relevant links
<ul>
  <li>
    <a href="https://github.com/JRequeijo/mHouseFramework">mHouse Framework Official Repository</a>
  </li>
  <li>
    <a href="https://github.com/JRequeijo/mHouseFramework/tree/master/docs/Cloud%20Platform">Cloud Platform Official Documentation</a>
  </li>
  <li>
    <a href="https://github.com/JRequeijo/mHouseFramework/tree/master/docs/Home%20Server">Home Server Official Documentation</a>
  </li>
  <li>
    <a href="https://github.com/JRequeijo/mHouseFramework/tree/master/docs/Endpoints">Endpoints Official Documentation</a>
  </li>
</ul>
