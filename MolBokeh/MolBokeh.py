from bokeh.plotting import figure, show, output_notebook
from bokeh.models import ColumnDataSource, HoverTool
import pandas as pd
from typing import Union

import base64
from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

class MolBokeh:
    def __init__(self):
        self._dfwithimg = None

    def add_molecule(self, fig, source:ColumnDataSource, smilesColName:str, hoverAdditionalInfo:Union[None, list]=None,molSize:tuple=(150,150)):
        """
        Add molecules images inside bokeh charts.

        Args:
            fig (bokeh object): Bokeh chart.
            source (ColumnDataSource): Bokehs data type used to built chart.
            smilesColName (str): Columns name that contain smiles.
            hoverAdditionalInfo (None | list): List of colnames that will show in hover.
            molSize (tuple): Size of molecules img.
        """

        UsersDF = pd.DataFrame(source.data) #geting users df as dataframe
        dfwithMolImg = self.__makingMoleculesImg(df=UsersDF,smilesColName=smilesColName,molSize=molSize)      
        fig_ = self.__cleanOriginalHover(fig=fig)        
        source.data = dfwithMolImg.copy() #update original data with base64 imgs
        hoverhtml = self.__makingHTML2hover(molimgColName='Mol_IMGSVG',
                                            hoverAdditionalInfo=hoverAdditionalInfo,
                                            molSize=molSize,)
        fig_ = self.__applyHover2fig(fig=fig_,hoverhtml=hoverhtml)       
        
        self._dfwithimg = dfwithMolImg.copy()
        return fig_

    def __applyHover2fig(self,fig,hoverhtml:str):
        """
        Apply hover inside bokeh charts.
        """
        fig_ = fig
        hover = HoverTool(tooltips=hoverhtml)
        fig_.add_tools(hover)
        return fig_

    def __makingMoleculesImg(self, df:pd.DataFrame,smilesColName:str,molSize:tuple):
        """
        This function creates the images and encodes them as a base64 string, it is added as a new column of the dataframe.
        """
        df_ = df.copy()
        df_['Mol_IMGSVG'] = df_[smilesColName].apply(lambda x: MolBokeh.smiTosvg(x,toHTMLformat=False,molSize=molSize))
        return df_

    def __makingHTML2hover(self,
                           molimgColName:str,
                           hoverAdditionalInfo:Union[None, int]=None,
                           molSize:tuple=(150,150)):
        """
        This function creates the HTML code that will be used as the bokeh hover.
        """
        if hoverAdditionalInfo == None:
            tooltips = f"""
            <div>
                <img src="@{molimgColName}" alt="Imagem" style="width: {molSize[0]}px; height: {molSize[0]}px;">
            </div>
            """
        else:
            tagsinfo2html = '\n'.join([f'<p style="text-align: center;"><strong>{colnames}:</strong> @{colnames}</p>' for colnames in hoverAdditionalInfo])

            tooltips = f"""
            <div>
                <img src="@{molimgColName}" alt="Imagem" style="width: {molSize[0]}px; height: {molSize[0]}px;">
                {tagsinfo2html}                
            </div>
            """
        
        return tooltips 

    def __cleanOriginalHover(self,fig):
        """
        This function deletes the original hover if it exists.
        """
        fig_ = fig
        for tool in fig_.tools:
            if isinstance(tool, HoverTool):
                fig_.tools.remove(tool)
        
        return fig_
    
    @staticmethod
    def smiTosvg(smi, molSize = (320,320), kekulize = True,toHTMLformat:bool = False):
        """
        This function generate a molecule img from smiles and return as html tag or pure base64 format.
        """
        mol = Chem.MolFromSmiles(smi)
        mc = Chem.Mol(mol.ToBinary())
        if kekulize:
            try:
                Chem.Kekulize(mc)
            except:
                mc = Chem.Mol(mol.ToBinary())
        if not mc.GetNumConformers():
            rdDepictor.Compute2DCoords(mc)
        drawer = rdMolDraw2D.MolDraw2DSVG(molSize[0],molSize[1])
        drawer.DrawMolecule(mc)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText().replace('svg:','')

        b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
        if toHTMLformat:            
            html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
        else:
            html = f"data:image/svg+xml;base64,{b64}"
            

        return html
        