import functools
from functools import lru_cache

from scopeserver.utils import DataFileHandler as dfh

class SearchSpace(dict):

    '''
    SearchSpace class is used to build the search space that contain all the queryable elements:
    - Homo sapiens to Drosophila melanogaster gene mappings
    - Mus musculus to Drosophila melanogaster gene mappings
    - Genes
    - Clusterings (inferred from e.g.: Seurat, ...)
    - Regulons (inferred from SCENIC)
    - Annotations
    - Metrics
    '''

    def __init__(self, loom, cross_species=''):
        dict.__init__(self)
        self.loom = loom
        self.cross_species = cross_species
        self.species, self.gene_mappings = loom.infer_species()

    def add_element(self, element, element_type):
        if element_type == 'gene' and self.cross_species == '' and len(self.gene_mappings) > 0:
            if self.gene_mappings[element] != element:
                self[('{0}'.format(str(element)).casefold(), element, element_type)] = self.gene_mappings[element]
            else:
                self[(element.casefold(), element, element_type)] = element
        else:
            self[(element.casefold(), element, element_type)] = element

    def add_elements(self, elements, element_type):
        for element in elements:
            self.add_element(element=element, element_type=element_type)
    
    def build(self):
        if self.cross_species != '':
            self.add_cross_species_genes()
        else:
            if self.loom.has_meta_data():
                self.meta_data = self.loom.get_meta_data()
            # Add genes to the search space
            self.add_genes()
            # Add clusterings to the search space if present in .loom
            if self.loom.has_md_clusterings():
                self.add_clusterings()
            # Add regulons to the search space if present in .loom
            if self.loom.has_regulons_AUC():
                self.add_regulons()
            # Add annotations to the search space if present in .loom
            if self.loom.has_md_annotations():
                self.add_annotations()
            # Add metrics to the search space if present in .loom
            if self.loom.has_md_metrics():
                self.add_metrics()
        return self

    def add_cross_species_genes(self):
        if self.cross_species == 'hsap' and self.species == 'dmel':
            self.add_elements(elements=dfh.DataFileHandler.hsap_to_dmel_mappings.keys(), element_type='gene')
        elif self.cross_species == 'mmus' and self.species == 'dmel':
            self.add_elements(elements=dfh.DataFileHandler.mmus_to_dmel_mappings.keys(), element_type='gene')

    def add_genes(self):
        # Add genes to search space
        if len(self.gene_mappings) > 0:
            genes = set(self.loom.get_genes())
            shrink_mappings = set([x for x in dfh.DataFileHandler.dmel_mappings.keys() if x in genes or dfh.DataFileHandler.dmel_mappings[x] in genes])
            self.add_elements(elements=shrink_mappings, element_type='gene')
        else:
            self.add_elements(elements=self.loom.get_genes(), element_type='gene')
    
    def add_clusterings(self):
        for clustering in self.meta_data['clusterings']:
            all_clusters = ['All Clusters']
            for cluster in clustering['clusters']:
                all_clusters.append(cluster['description'])
            self.add_elements(elements=all_clusters, element_type='Clustering: {0}'.format(clustering['name']))
    
    def add_regulons(self):
        self.add_elements(elements=self.loom.get_regulons_AUC().dtype.names, element_type='regulon')

    def add_annotations(self):
        annotations = []
        for annotation in self.meta_data['annotations']:
            annotations.append(annotation['name'])
        self.add_elements(elements=annotations, element_type='annotation')
    
    def add_metrics(self):
        metrics = []
        for metric in self.meta_data['metrics']:
            metrics.append(metric['name'])
        self.add_elements(elements=metrics, element_type='metric')

    