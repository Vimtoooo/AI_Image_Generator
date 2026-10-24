import copy
import json
import pytest
from comfy_generator.models import NodeMapping, freeze
from comfy_generator.payload_mgr import PayloadManager, WorkflowError, AmbiguousWorkflowError, detect_node_mapping, parse_workflow_json, validate_node_mapping
from utils.formatting_utils import format_positive_prompt


def chain(prefix='x'):
    m = NodeMapping(*(prefix + r for r in ('sampler','checkpoint','latent','positive','negative','decode','save')))
    def node(kind, **inputs):
        return {'class_type': kind, 'inputs': inputs}
    return m, {
        m.checkpoint: node('CheckpointLoaderSimple', ckpt_name='fictional.safetensors'),
        m.latent: node('EmptyLatentImage', width=512, height=512, batch_size=1),
        m.positive: node('CLIPTextEncode', clip=[m.checkpoint,1], text='global'),
        m.negative: node('CLIPTextEncode', clip=[m.checkpoint,1], text='blur'),
        m.sampler: node('KSampler', model=[m.checkpoint,0], latent_image=[m.latent,0], positive=[m.positive,0], negative=[m.negative,0], seed=42, steps=20, cfg=7.0, sampler_name='euler', scheduler='normal', denoise=1.0),
        m.decode: node('VAEDecode', samples=[m.sampler,0], vae=[m.checkpoint,2]),
        m.save: node('SaveImage', images=[m.decode,0], filename_prefix='fictional'),
    }


def test_changed_ids_and_extraction():
    m,g=chain()
    g['extra']={'class_type':'UnrelatedCustom','inputs':{}}
    assert detect_node_mapping(g)==m
    p=PayloadManager(g).current_payload
    assert set(p)==set(g)-{'extra'}
    assert p[m.sampler]['inputs']['denoise']==1.0


def test_ambiguity_requires_explicit_mapping():
    m,g=chain(); other,h=chain('y'); g.update(h)
    with pytest.raises(AmbiguousWorkflowError) as exc:
        PayloadManager(g)
    assert exc.value.candidates==(m,other)
    assert PayloadManager(g,other).current_payload==h
    g[m.positive]['inputs']['clip']=[other.checkpoint,1]
    with pytest.raises(WorkflowError,match='positive.clip'):
        PayloadManager(g,m)


@pytest.mark.parametrize('text',['{','[]','{}','{"nodes": [], "links": []}','{"3":{"inputs":{}}}'])
def test_invalid_json_shape(text):
    with pytest.raises(WorkflowError,match='API-format'):
        parse_workflow_json(text)


def test_json_roundtrip():
    m,g=chain()
    assert detect_node_mapping(parse_workflow_json(json.dumps(g)))==m


@pytest.mark.parametrize('role,field,slot', [('sampler','model',1),('sampler','latent_image',1),('sampler','positive',1),('sampler','negative',1),('positive','clip',0),('negative','clip',0),('decode','samples',1),('decode','vae',0),('save','images',1)])
def test_wrong_slot(role,field,slot):
    m,g=chain(); g[getattr(m,role)]['inputs'][field][1]=slot
    with pytest.raises(WorkflowError,match=role):
        validate_node_mapping(g,m)


@pytest.mark.parametrize('batch',[0,2,True,1.0,'1'])
def test_batch(batch):
    m,g=chain(); g[m.latent]['inputs']['batch_size']=batch
    with pytest.raises(WorkflowError,match='latent.batch_size'):
        PayloadManager(g)


def test_unsupported_topology():
    m,g=chain(); g[m.sampler]['class_type']='CustomSampler'
    with pytest.raises(WorkflowError,match='sampler'):
        PayloadManager(g)
    g[m.sampler]['class_type']='KSampler'; g[m.sampler]['inputs']['custom']=[m.checkpoint,0]
    with pytest.raises(WorkflowError,match='sampler.custom'):
        PayloadManager(g)


def test_distinct_roles():
    m,g=chain()
    invalid=NodeMapping(m.sampler,m.checkpoint,m.latent,m.positive,m.positive,m.decode,m.save)
    with pytest.raises(WorkflowError,match='distinct'):
        PayloadManager(g,invalid)


def test_frozen_and_independent_payloads():
    m,g=chain(); original=copy.deepcopy(g); manager=PayloadManager(freeze(g))
    first=manager.build_scene_payload('one','style','')
    first[m.sampler]['inputs']['model'][0]='corrupt'
    first[m.negative]['inputs']['text']='corrupt'
    second=manager.build_scene_payload('two','','avoid')
    assert second[m.positive]['inputs']['text']=='two'
    assert second[m.negative]['inputs']['text']=='avoid'
    assert second[m.sampler]['inputs']['model']==[m.checkpoint,0]
    assert manager.base_workflow==manager.current_payload==original==g


@pytest.mark.parametrize('positive,negative',[('global','avoid'),('',''),('global',''),('','avoid')])
def test_prompt_combinations(positive,negative):
    m,g=chain(); p=PayloadManager(g).build_scene_payload('scene',positive,negative)
    expected='global\nSCENE TO CREATE: scene' if positive else 'scene'
    assert p[m.positive]['inputs']['text']==expected==format_positive_prompt(positive,'scene')
    assert p[m.negative]['inputs']['text']==negative


def test_legacy_updates_and_reset():
    m,g=chain(); manager=PayloadManager(g)
    assert manager.update_sampler('other',['other']).update_negative_prompt('') is manager
    manager.update_positive_prompt('new').update_seed(9).update_steps(10).update_cfg(6.0)
    manager.update_resolution(1024,576).update_checkpoint_model('new',['new'])
    p=manager.current_payload
    assert p[m.sampler]['inputs']['sampler_name']=='other'
    assert 'sampler_name' not in p[m.checkpoint]['inputs']
    assert p[m.sampler]['inputs']['scheduler']=='normal'
    assert p[m.sampler]['inputs']['seed']==9
    assert p[m.negative]['inputs']['text']==''
    assert p[m.latent]['inputs']['width']==1024
    manager.reset_payload()
    assert manager.current_payload==g
