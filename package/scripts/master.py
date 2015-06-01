import sys, os, pwd, signal, time
from resource_management import *
from subprocess import call

class Master(Script):
  def install(self, env):
    # Install packages listed in metainfo.xml
    self.install_packages(env)
    self.configure(env)
    import params

    Execute('echo clusterHostInfo contents:' +  str(', '.join(params.clusterHostInfo)))
    
    #e.g. /var/lib/ambari-agent/cache/stacks/HDP/2.2/services/kdc-stack/package
    service_packagedir = os.path.realpath(__file__).split('/scripts')[0] 
    Execute('/bin/cp -f '+service_packagedir+'/templates/krb5.conf /etc')

    Execute('sed -i "s/kerberos.example.com/'+params.kdc_host+'/g" /etc/krb5.conf')    
    Execute('sed -i "s/EXAMPLE.COM/'+params.kdc_realm+'/g" /etc/krb5.conf')
    Execute('sed -i "s/example.com/'+params.kdc_domain+'/g" /etc/krb5.conf')
    

    Execute('echo "'+params.kdb_password+'" > passwd.txt')
    Execute('echo "'+params.kdb_password+'" >> passwd.txt')
    Execute('echo >> passwd.txt')
    Execute('kdb5_util create -s < passwd.txt')
    Execute('rm passwd.txt')

    Execute('/etc/rc.d/init.d/krb5kdc start')
    Execute('/etc/rc.d/init.d/kadmin start')

    Execute('chkconfig krb5kdc on')
    Execute('chkconfig kadmin on')

    Execute('echo "'+params.kdc_adminpassword+'" > passwd.txt')
    Execute('echo "'+params.kdc_adminpassword+'" >> passwd.txt')
    Execute('echo >> passwd.txt')
    Execute('kadmin.local -q "addprinc '+params.kdc_admin+'" < passwd.txt')
    Execute('rm passwd.txt')

    Execute('echo "*/admin@'+params.kdc_realm+' *" > /var/kerberos/krb5kdc/kadm5.acl')

    #Execute('/etc/rc.d/init.d/krb5kdc restart')
    #Execute('/etc/rc.d/init.d/kadmin restart')


  def configure(self, env):
    import params
    env.set_params(params)

  def stop(self, env):
    import params
    Execute('service krb5kdc stop')
    Execute('service kadmin stop')
          
  def start(self, env):
    import params
    Execute('service krb5kdc start')
    Execute('service kadmin start')
	

  def status(self, env):
    import params
    Execute('service krb5kdc status')

    
if __name__ == "__main__":
  Master().execute()
